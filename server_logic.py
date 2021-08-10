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

# seek closest food
def hungry(data):
    if status: print('HUNGRY! SEEKING FOOD.')
    grid = build_map(data)
    close_food = closest_food(grid, data)
    move = astar(data, grid, close_food, 'food')
    return move

# follow own tail to kill time
def kill_time(data):
    if status: print('COOL. KILLING TIME.')
    grid = build_map(data)
    tail = get_tail(data)
    move = astar(data, grid, tail, 'my_tail')
    return move

# astar pathfinding, from https://github.com/vllry/checkfront-battlesnake
def astar(data, grid, destination, mode):
    global debug
    if debug:
        print("map:")
        print_map(grid)
    if status: print('MAP BUILT! CALCULATING PATH...')
    #destination = get_coords(destination)
    search_scores = build_astar_grid(data, grid)
    open_set = []
    closed_set = []
    # set start location to current head location
    start = current_location(data)
    # on first 3 moves, point to closest food
    if data['turn'] < INITIAL_FEEDING:
        destination = closest_food(grid, data)
    if debug:
        print('astar destination: ' + str(destination))
        # print("astar grid before search:")
        # print_f_scores(search_scores)
    open_set.append(start)
    # while openset is NOT empty keep searching
    while open_set:
        lowest_cell = [9999, 9999] # x, y
        lowest_f = 9999
        # find cell with lowest f score
        for cell in open_set:
            if search_scores[cell[0]][cell[1]].f < lowest_f: # CONSIDER CHANGING TO <= AND THEN ALSO COMPARING G SCORES
                lowest_f = search_scores[cell[0]][cell[1]].f
                lowest_cell = cell
        # found path to destination
        if lowest_cell[0] == destination[0] and lowest_cell[1] == destination[1]:
            if status: print('FOUND A PATH!')
            if debug:
                print("astar grid after search success:")
                print_f_scores(search_scores)
            # retrace path back to origin to find optimal next move
            temp = lowest_cell
            if debug:
                print('astar start pos: ' + str(start))
            while search_scores[temp[0]][temp[1]].previous[0] != start[0] or search_scores[temp[0]][temp[1]].previous[1] != start[1]:
                temp = search_scores[temp[0]][temp[1]].previous
            # get direction of next optimal move
            if debug: print('astar next move: ' + str(temp))
            next_move = calculate_direction(start, temp, grid, data)
            return next_move
        # else continue searching
        current = lowest_cell
        current_cell = search_scores[current[0]][current[1]]
        # update sets
        open_set.remove(lowest_cell)
        closed_set.append(current)
        # check every viable neighbor to current cell
        for neighbor in search_scores[current[0]][current[1]].neighbors:
            neighbor_cell = search_scores[neighbor[0]][neighbor[1]]
            if neighbor[0] == destination[0] and neighbor[1] == destination[1]:
                if status: print('FOUND A PATH! (neighbor)')
                neighbor_cell.previous = current
                if debug:
                    print("astar grid after search success:")
                    print_f_scores(search_scores)
                # retrace path back to origin to find optimal next move
                temp = neighbor
                if debug:
                    print('astar start pos: ' + str(start))
                while search_scores[temp[0]][temp[1]].previous[0] != start[0] or search_scores[temp[0]][temp[1]].previous[1] != start[1]:
                    temp = search_scores[temp[0]][temp[1]].previous
                # get direction of next optimal move
                if debug: print('astar next move: ' + str(temp))
                next_move = calculate_direction(start, temp, grid, data)
                return best_move(next_move, data, grid)
            # check if neighbor can be moved to
            if neighbor_cell.state < SNAKE_BODY:
                # check if neighbor has already been evaluated
                if neighbor not in closed_set:# and grid[neighbor[0]][neighbor[1]] <= FOOD:
                    temp_g = current_cell.g + 1
                    shorter = True
                    # check if already evaluated with lower g score
                    if neighbor in open_set:
                        if temp_g > neighbor_cell.g: # CHANGE TO >= ??
                            shorter = False
                    # if not in either set, add to open set
                    else:
                        #if debug: print('neighbor: ' + str(grid[neighbor[0]][neighbor[1]]))
                        open_set.append(neighbor)
                    # this is the current best path, record it
                    if shorter:
                        neighbor_cell.g = temp_g
                        neighbor_cell.h = get_distance(neighbor, destination)
                        neighbor_cell.f = neighbor_cell.g + neighbor_cell.h
                        neighbor_cell.previous = current
        # inside for neighbor
    # inside while open_set
    # if reach this point and open set is empty, no path
    if not open_set:
        if status: print('COULD NOT FIND PATH!')
        if debug:
            print("astar grid after search failure:")
            print_f_scores(search_scores)

        move = 2
        if mode == 'food':
            tail = get_tail(data)
            move = astar(data, grid, tail, 'my_tail')
        
        return best_move(move, data, grid)



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
    my_body = data["you"]["body"]  # A list of x/y coordinate dictionaries like [ {"x": 0, "y": 0}, {"x": 1, "y": 0}, {"x": 2, "y": 0} ]

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

    
    
    # TODO Using information from 'data', don't let your Battlesnake pick a move that would hit its own body

    # TODO: Using information from 'data', don't let your Battlesnake pick a move that would collide with another Battlesnake

    # TODO: Using information from 'data', make your Battlesnake move towards a piece of food on the board

    # Choose a random direction from the remaining possible_moves to move in, and then return that move
    move = random.choice(possible_moves)
    # TODO: Explore new strategies for picking a move that are better than random

    print(f"{data['game']['id']} MOVE {data['turn']}: {move} picked from all valid options in {possible_moves}")

    return move
