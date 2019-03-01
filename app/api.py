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

def create_board(height, width, value):
    return [[value for x in range(width)] for y in range(height)]

def populate_food(play_board, food):
    for coord in food:
        x = coord['x']
        y = coord['y']
        play_board[y][x] = FOOD

def populate_snakes(play_board, snakes):
    for i in range(len(snakes)):
        snake_value = i+2
        snake_body = snakes[i]['body']
        for coord in snake_body:
            x = coord['x']
            y = coord['y']
            play_board[y][x] = snake_value

def populate_you(play_board, you):
    snake_body = you['body']
    for coord in snake_body:
        x = coord['x']
        y = coord['y']
        play_board[y][x] = YOU

def print_board(board):
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
    play_board = create_board(height, width, EMPTY)

    food = data['board']['food']
    populate_food(play_board, food)
    snakes = data['board']['snakes']
    populate_snakes(play_board, snakes)
    you = data['you']
    populate_you(play_board, you)
    print_board(play_board)

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
