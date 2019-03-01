import json
from bottle import HTTPResponse

EMPTY = 0
YOU = 1
FOOD = 9

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

def _create_board(height, width, value):
    return [[value for x in range(width)] for y in range(height)]

def _populate_food(board, food):
    for coord in food:
        x = coord['x']
        y = coord['y']
        board[y][x] = FOOD

def _extract_enemy_you(snakes, you):
    enemy_snakes = []
    for snake in snakes:
        if snake['id'] != you['id']:
            enemy_snakes.append(snake)
    return [enemy_snakes, you]

def _populate_snakes(board, enemy_snakes, you_snake):
    for i in range(len(enemy_snakes)):
        snake_value = i+2
        snake_body = enemy_snakes[i]['body']
        for coord in snake_body:
            x = coord['x']
            y = coord['y']
            board[y][x] = snake_value

    snake_body = you_snake['body']
    for coord in snake_body:
        x = coord['x']
        y = coord['y']
        board[y][x] = YOU

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

def move_process(data):
    height = data['board']['height']
    width = data['board']['width']
    board = _create_board(height, width, EMPTY)

    food = data['board']['food']
    _populate_food(board, food)
    snakes = data['board']['snakes']
    you = data['you']
    enemy_snakes, you_snake = _extract_enemy_you(snakes, you)
    print('enemy: '+str(enemy_snakes))
    print('you: '+str(you_snake))
    _populate_snakes(board, enemy_snakes, you_snake)

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
