import json
from bottle import HTTPResponse

EMPTY = 0
YOU = 1
FOOD = 9
TAIL = 10
OTHER_TAIL = 11
DEADEND = 12

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
        coord = snake_body[-1]
        x = coord['x']
        y = coord['y']
        board[y][x] = OTHER_TAIL

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
    print('+---'*len(board[0])+'+')
    for row in board:
        for column in row:
            print('|'),
            if column != 0:
                print(column),
            else:
                print(' '),
        print('|')
        print('+---'*len(board[0])+'+')

def _get_cell(board, height, width, x, y):
    if 0 <= x and x <= width-1 and 0 <= y and y <= height-1:
        cell = board[y][x]
        if cell in [EMPTY, FOOD, TAIL]:
            return cell
    return None

def _get_all_cell(board, height, width, x, y):
    if 0 <= x and x <= width-1 and 0 <= y and y <= height-1:
        cell = board[y][x]
        if cell not in range(1,9):
            return cell
    return None

def _mark_deadend(board, height, width, snake_length):
    area_list = []
    visited = [[False for x in range(width)] for y in range(height)]

    # sweep
    area = []
    for x in range(width):
        for y in range(height):
            if visited[y][x]:
                continue
            visited[y][x] = True
            if _get_cell(board, height, width, x, y) == None:
                continue
            area.append([x,y])
            neighbor_list = [[x,y]]
            while len(neighbor_list) > 0:
                new_neighbor_list = []
                for x, y in neighbor_list:
                    if _get_cell(board, height, width, x, y-1) != None and not visited[y-1][x]:
                        visited[y-1][x] = True
                        area.append([x,y-1])
                        new_neighbor_list.append([x,y-1])
                    if _get_cell(board, height, width, x, y+1) != None and not visited[y+1][x]:
                        visited[y+1][x] = True
                        area.append([x,y+1])
                        new_neighbor_list.append([x,y+1])
                    if _get_cell(board, height, width, x-1, y) != None and not visited[y][x-1]:
                        visited[y][x-1] = True
                        area.append([x-1,y])
                        new_neighbor_list.append([x-1,y])
                    if _get_cell(board, height, width, x+1, y) != None and not visited[y][x+1]:
                        visited[y][x+1] = True
                        area.append([x+1,y])
                        new_neighbor_list.append([x+1,y])
                neighbor_list = new_neighbor_list
            area_list.append(area)
            area = []

    # mark
    for area in area_list:
        if len(area) < snake_length:
            for x, y in area:
                board[y][x] = DEADEND + len(area)

def _generate_path_list(board, height, width, head_x, head_y):
    food_path_list = []
    tail_path_list = []
    empty_path_list = []
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
            if cell == EMPTY:
                empty_path_list.append(path[:])
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

    return [food_path_list,tail_path_list,empty_path_list]

def _is_good_path(distance_matrix, path):
    is_good_path = True
    for i in range(len(path)):
        distance = i+1
        direction, x, y = path[i]
        if distance_matrix[y][x] <= distance:
            is_good_path = False
    return is_good_path

def _find_shortest(distance_matrix, path_list):
    # find the shortest good path
    min_path = None
    for path in path_list:
        if _is_good_path(distance_matrix, path):
            if min_path == None:
                min_path = path
            elif len(min_path) > len(path):
                min_path = path

    if min_path != None:
        direction, x, y = min_path[0]
        return direction
    return None

def _find_longest(distance_matrix, path_list):
    # find the longest good path
    max_path = None
    for path in path_list:
        if _is_good_path(distance_matrix, path):
            if max_path == None:
                max_path = path
            elif len(max_path) < len(path):
                max_path = path

    if max_path != None:
        direction, x, y = max_path[0]
        return direction
    return None

def _is_tangled(head_x, head_y, you_snake):
    x_array = [coord['x'] for coord in you_snake['body']]
    y_array = [coord['y'] for coord in you_snake['body']]
    num_sides = 0
    if min(x_array) < head_x:
        num_sides += 1
    if max(x_array) > head_x:
        num_sides += 1
    if min(y_array) < head_y:
        num_sides += 1
    if max(y_array) > head_y:
        num_sides += 1
    return num_sides >= 3

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
    _mark_deadend(board, height, width, len(you_snake['body']))
    food_path_list, tail_path_list, empty_path_list = _generate_path_list(board, height, width, head_x, head_y)

    direction = None

    direction = _find_shortest(distance_matrix, food_path_list)
    if direction == None:
        direction = _find_shortest(distance_matrix, tail_path_list)
    if direction == None:
        direction = _find_shortest(distance_matrix, empty_path_list)

    # when all else failed
    if direction == None:
        move_list = []
        move_list += [[UP, _get_all_cell(board, height, width, head_x, head_y-1)]]
        move_list += [[DOWN, _get_all_cell(board, height, width, head_x, head_y+1)]]
        move_list += [[LEFT, _get_all_cell(board, height, width, head_x-1, head_y)]]
        move_list += [[RIGHT, _get_all_cell(board, height, width, head_x+1, head_y)]]
        max_cell = None
        for current_direction, current_cell in move_list:
            if current_cell == None:
                continue
            if max_cell == None or max_cell < current_cell:
                direction = current_direction
                max_cell = current_cell

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
