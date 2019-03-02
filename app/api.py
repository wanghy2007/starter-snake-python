import json
from bottle import HTTPResponse

EMPTY = 0
YOU = 1
FOOD = 9
TAIL = 10

UP = "up"
DOWN = "down"
LEFT = "left"
RIGHT = "right"

def ping_response():
    return HTTPResponse(
        status=200
    )

def start_response(color):
    assert type(color) is str, \
        "Color value must be string"

    return HTTPResponse(
        status=200,
        headers={
            "Content-Type": "application/json"
        },
        body=json.dumps({
            "color": color
        })
    )

def _extract_enemy_you(snakes, you):
    enemy_snakes = []
    for snake in snakes:
        if snake['id'] != you['id']:
            enemy_snakes.append(snake)
    return [enemy_snakes, you]

def _create_board(height, width, food, enemy_snakes, you_snake):
    # create board
    board = [[EMPTY for x in range(width)] for y in range(height)]

    # populate food
    for coord in food:
        x = coord['x']
        y = coord['y']
        board[y][x] = FOOD

    # populate enemy snakes
    for i in range(len(enemy_snakes)):
        snake_value = i+2
        snake_body = enemy_snakes[i]['body']
        for coord in snake_body:
            x = coord['x']
            y = coord['y']
            board[y][x] = snake_value

    # populate you snake
    snake_body = you_snake['body']
    for coord in snake_body:
        x = coord['x']
        y = coord['y']
        board[y][x] = YOU

    # mark around tail to avoid colliding into ourselves
    coord = snake_body[-1]
    x = coord['x']
    y = coord['y']
    if _get_cell(board, height, width, x, y-1) == EMPTY:
        board[y-1][x] = TAIL
    if _get_cell(board, height, width, x, y+1) == EMPTY:
        board[y+1][x] = TAIL
    if _get_cell(board, height, width, x-1, y) == EMPTY:
        board[y][x-1] = TAIL
    if _get_cell(board, height, width, x+1, y) == EMPTY:
        board[y][x+1] = TAIL

    return board

def _calculate_distance(x, y, enemy_snake_heads):
    distance_list = [abs(x-head['x'])+abs(y-head['y']) for head in enemy_snake_heads]
    return min(distance_list)

def _create_distance_matrix(height, width, enemy_snakes):
    distance_matrix = [[width+height for x in range(width)] for y in range(height)]
    enemy_snake_heads = []
    for snake in enemy_snakes:
        if len(snake['body']) > 0:
            head = snake['body'][0]
            enemy_snake_heads.append(head)

    if len(enemy_snake_heads) > 0:
        for x in range(width):
            for y in range(height):
                distance_matrix[y][x] = _calculate_distance(x, y, enemy_snake_heads)

    return distance_matrix

def _print_board(board):
    print('+---'*len(board)+'+')
    for row in board:
        for column in row:
            print('|'),
            if column != 0:
                print(column),
            else:
                print(' '),
        print('|')
        print('+---'*len(board)+'+')

def _get_cell(board, height, width, x, y):
    if 0 <= x and x <= width-1 and 0 <= y and y <= height-1:
        cell = board[y][x]
        if cell in [EMPTY, FOOD, TAIL]:
            return cell
    return None

def _generate_path_list(board, height, width, head_x, head_y):
    food_path_list = []
    tail_path_list = []
    visited = [[False for x in range(width)] for y in range(height)]

    # populate initial path list
    path_list = []
    if _get_cell(board, height, width, head_x, head_y-1) != None:
        visited[head_x][head_y-1] = True
        path_list.append([[UP, head_x, head_y-1]])
    if _get_cell(board, height, width, head_x, head_y+1) != None:
        visited[head_x][head_y+1] = True
        path_list.append([[DOWN, head_x, head_y+1]])
    if _get_cell(board, height, width, head_x-1, head_y) != None:
        visited[head_x-1][head_y] = True
        path_list.append([[LEFT, head_x-1, head_y]])
    if _get_cell(board, height, width, head_x+1, head_y) != None:
        visited[head_x+1][head_y] = True
        path_list.append([[RIGHT, head_x+1, head_y]])

    # visit neighbors
    while len(path_list) > 0:
        new_path_list = []
        for path in path_list:
            direction, x, y = path[-1]
            cell = _get_cell(board, height, width, x, y)
            if cell == FOOD:
                food_path_list.append(path[:])
            if cell == TAIL:
                tail_path_list.append(path[:])
            if _get_cell(board, height, width, x, y-1) != None and not visited[y-1][x]:
                visited[y-1][x] = True
                new_path_list.append(path[:]+[[UP, x, y-1]])
            if _get_cell(board, height, width, x, y+1) != None and not visited[y+1][x]:
                visited[y+1][x] = True
                new_path_list.append(path[:]+[[DOWN, x, y+1]])
            if _get_cell(board, height, width, x-1, y) != None and not visited[y][x-1]:
                visited[y][x-1] = True
                new_path_list.append(path[:]+[[LEFT, x-1, y]])
            if _get_cell(board, height, width, x+1, y) != None and not visited[y][x+1]:
                visited[y][x+1] = True
                new_path_list.append(path[:]+[[RIGHT, x+1, y]])
        path_list = new_path_list

    return [food_path_list,tail_path_list]

def _find_food(board, distance_matrix, food_path_list):
    if len(food_path_list) == 0:
        return None
    if len(food_path_list) == 1:
        direction, x, y = food_path_list[0][0]
        return direction

    # find the shortest good path
    min_path = None
    for food_path in food_path_list:
        is_good_path = True
        for i in range(len(food_path)):
            distance = i+1
            direction, x, y = food_path[i]
            if distance_matrix[y][x] <= distance:
                is_good_path = False
                break
        if is_good_path:
            if min_path == None:
                min_path = food_path
            elif len(min_path) > len(food_path):
                min_path = food_path

    if min_path != None:
        direction, x, y = min_path[0]
        return direction
    return None

def _find_tail(tail_path_list):
    if len(tail_path_list) == 0:
        return None
    direction, x, y = tail_path_list[0][0]
    return direction

def move_process(data):
    height = data['board']['height']
    width = data['board']['width']
    food = data['board']['food']
    enemy_snakes, you_snake = _extract_enemy_you(
        data['board']['snakes'],
        data['you']
    )
    board = _create_board(height, width, food, enemy_snakes, you_snake)

    distance_matrix = _create_distance_matrix(height, width, enemy_snakes)
    #_print_board(distance_matrix)

    head_x = you_snake['body'][0]['x']
    head_y = you_snake['body'][0]['y']
    food_path_list, tail_path_list = _generate_path_list(board, height, width, head_x, head_y)

    direction = _find_food(board, distance_matrix, food_path_list)

    if direction == None:
        direction = _find_tail(tail_path_list)

    # when all else failed
    if direction == None and _get_cell(board, height, width, head_x, head_y-1):
        direction = UP
    if direction == None and _get_cell(board, height, width, head_x, head_y+1):
        direction = DOWN
    if direction == None and _get_cell(board, height, width, head_x-1, head_y):
        direction = LEFT
    if direction == None and _get_cell(board, height, width, head_x+1, head_y):
        direction = RIGHT

    return direction

def move_response(move):
    assert move in ['up', 'down', 'left', 'right'], \
        "Move must be one of [up, down, left, right]"

    return HTTPResponse(
        status=200,
        headers={
            "Content-Type": "application/json"
        },
        body=json.dumps({
            "move": move
        })
    )

def end_response():
    return HTTPResponse(
        status=200
    )
