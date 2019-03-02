import json
from bottle import HTTPResponse

EMPTY = 0
YOU = 1
FOOD = 9

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
        return board[y][x]
    return None

def _generate_food_path_list(board, height, width, head_x, head_y):
    food_path_list = []
    visited = [[False for x in range(width)] for y in range(height)]

    # populate initial neighbor list
    neighbor_list = []
    if _get_cell(board, height, width, head_x, head_y-1) != None:
        neighbor_list.append([[UP], head_x, head_y-1])
    if _get_cell(board, height, width, head_x, head_y+1) != None:
        neighbor_list.append([[DOWN], head_x, head_y+1])
    if _get_cell(board, height, width, head_x-1, head_y) != None:
        neighbor_list.append([[LEFT], head_x-1, head_y])
    if _get_cell(board, height, width, head_x+1, head_y) != None:
        neighbor_list.append([[RIGHT], head_x+1, head_y])

    # visit neighbors
    while len(neighbor_list) > 0:
        for path, x, y in neighbor_list:
            if _get_cell(board, height, width, x, y) == FOOD:
                food_path_list.append(path[:])
            if _get_cell(board, height, width, x, y-1) != None:
                neighbor_list.append([path[:]+[UP], x, y-1])
            if _get_cell(board, height, width, x, y+1) != None:
                neighbor_list.append([path[:]+[DOWN], x, y+1])
            if _get_cell(board, height, width, x-1, y) != None:
                neighbor_list.append([path[:]+[LEFT], x-1, y])
            if _get_cell(board, height, width, x+1, y) != None:
                neighbor_list.append([path[:]+[RIGHT], x+1, y])

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
    _print_board(board)

    return 'left'

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
