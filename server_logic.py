import random
from typing import List, Dict

"""
This file can be a nice home for your move logic, and to write helper functions.

We have started this for you, with a function to help remove the 'neck' direction
from the list of possible moves!
"""


def avoid_my_neck(my_head: Dict[str, int], my_body: List[dict], possible_moves: List[str]) -> List[str]:
    """
    my_head: Dictionary of x/y coordinates of the Battlesnake head.
            e.g. {"x": 0, "y": 0}
    my_body: List of dictionaries of x/y coordinates for every segment of a Battlesnake.
            e.g. [ {"x": 0, "y": 0}, {"x": 1, "y": 0}, {"x": 2, "y": 0} ]
    possible_moves: List of strings. Moves to pick from.
            e.g. ["up", "down", "left", "right"]

    return: The list of remaining possible_moves, with the 'neck' direction removed
    """
    # for i in range(len)
    my_neck = my_body[1]  # The segment of body right after the head is the 'neck'

    if my_neck["x"] < my_head["x"]:  # my neck is left of my head
        possible_moves.remove("left")
    elif my_neck["x"] > my_head["x"]:  # my neck is right of my head
        possible_moves.remove("right")
    elif my_neck["y"] < my_head["y"]:  # my neck is below my head
        possible_moves.remove("down")
    elif my_neck["y"] > my_head["y"]:  # my neck is above my head
        possible_moves.remove("up")

    return possible_moves


def avoid_walls(my_head: Dict[str, int], possible_moves: List[str], board_height, board_width):
    # board_height and board_width == 3
    #    0,2 | 1,2 | 2,2
    #    0,1 | 1,1 | 2,1
    #    0,0 | 1,0 | 2,0
    if (my_head["y"] == board_height - 1):
        possible_moves.remove("up")
    if (my_head["x"] == board_width - 1):
        possible_moves.remove("right")
    if (my_head["y"] == 0):
        possible_moves.remove("down")
    if (my_head["x"] == 0):
        possible_moves.remove("left")


def populate_grid(grid: List[List[int]], data: dict, my_head: Dict[str, int], board_height):
    # need to get hazards at
    # 0 means that we can move to the spot
    # 1 means that snake dies if we move to the spot
    # 2 means that there is a froot on that spot
    # 4 is the player
    # TODO : ask if we want to switch to letters......
    grid[board_height - 1 - my_head["y"]][my_head["x"]] = 4
    hazards = data["board"]["hazards"]
    for hazard in hazards:
        grid[board_height - 1 - hazard["y"]][hazard["x"]] = 1
    my_id = data["you"]["id"]
    for snake in data["board"]["snakes"]:
        start_index = 0
        if snake["id"] == my_id:
            start_index = 1
        for i in range(start_index, snake["length"]):
            s_x, s_y = snake["body"][i]["x"], snake["body"][i]["y"]
            # note I am doing (board_height - 1 - s_y) to be consistent with having the 0,0 coordinate at bottom left corner
            grid[board_height - 1 - s_y][s_x] = 1


def filter_obstacles_close(grid: List[List[int]], my_head: Dict[str, int], possible_moves: List[str], board_height,
                           board_width):
    """
    this method will filter out the moves which are impossible to make if to hit body imidiatly
    """
    # i want to go over the moves that are avalible and check on the grid if it is possible ot
    my_x, my_y = my_head["x"], my_head["y"]
    cur_moves = [i for i in possible_moves]
    for move in possible_moves:
        x, y = 0, 0
        if move == "right":
            x = 1
        elif move == "left":
            x = -1
        elif move == "up":
            y = 1
        elif move == "down":
            y = -1
        if board_height - 1 - (my_y + y) == board_height or board_height - 1 - (my_y + y) < 0:
            cur_moves.remove(move)
            continue
        if my_x + x == board_width or my_x + x < 0:
            cur_moves.remove(move)
            continue
        if grid[board_height - 1 - my_y - y][my_x + x] != 0:
            # TODO change this is information in the grid is no longer a int
            cur_moves.remove(move)
    if len(cur_moves) == 0:
        return ["left"]
    return cur_moves


def choose_move(data: dict) -> str:
    """
    data: Dictionary of all Game Board data as received from the Battlesnake Engine.
    For a full example of 'data', see https://docs.battlesnake.com/references/api/sample-move-request

    return: A String, the single move to make. One of "up", "down", "left" or "right".

    Use the information in 'data' to decide your next move. The 'data' variable can be interacted
    with as a Python Dictionary, and contains all of the information about the Battlesnake board
    for each move of the game.

    """
    my_head = data["you"]["head"]  # A dictionary of x/y coordinates like {"x": 0, "y": 0}
    # A list of x/y coordinate dictionaries like [ {"x": 0, "y": 0}, {"x": 1, "y": 0}, {"x": 2, "y": 0} ]
    my_body = data["you"]["body"]

    # TODO: uncomment the lines below so you can see what this data looks like in your output!
    # print(f"~~~ Turn: {data['turn']}  Game Mode: {data['game']['ruleset']['name']} ~~~")
    # print(f"All board data this turn: {data}")
    # print(f"My Battlesnakes head this turn is: {my_head}")
    # print(f"My Battlesnakes body this turn is: {my_body}")

    possible_moves = ["up", "down", "left", "right"]

    # Don't allow your Battlesnake to move back in on it's own neck
    possible_moves = avoid_my_neck(my_head, my_body, possible_moves)

    # TODO: Using information from 'data', find the edges of the board and don't let your Battlesnake move beyond them
    board_height = data["board"]["height"]
    board_width = data["board"]["width"]
    our_board = [[0 for _ in range(board_width)] for _ in range(board_height)]
    populate_grid(our_board, data, my_head, board_height)
    possible_moves = filter_obstacles_close(our_board, my_head, possible_moves, board_height, board_width)
    # print(my_head)
    # print(board_height)
    # avoid_walls(my_head, possible_moves, board_height, board_width) # theoretically this method could be moved
    # bad_avoid_body(my_head, my_body, possible_moves)
    # if (my_head["y"] == board_height - 1):
    #     possible_moves = "left"

    # if (my_head["x"] == board_width - 1):
    #     possible_moves = "down"

    # TODO Using information from 'data', don't let your Battlesnake pick a move that would hit its own body

    # TODO: Using information from 'data', don't let your Battlesnake pick a move that would collide with another Battlesnake

    # TODO: Using information from 'data', make your Battlesnake move towards a piece of food on the board

    # Choose a random direction from the remaining possible_moves to move in, and then return that move
    move = random.choice(possible_moves)
    # TODO: Explore new strategies for picking a move that are better than random

    print(f"{data['game']['id']} MOVE {data['turn']}: {move} picked from all valid options in {possible_moves}")

    return move
