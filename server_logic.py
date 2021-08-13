import random
from typing import List, Dict

"""
This file can be a nice home for your move logic, and to write helper functions.

We have started this for you, with a function to help remove the 'neck' direction
from the list of possible moves!
"""

# board variables
debug = True
SPACE = 0
KILL_ZONE = 1
FOOD = 2
#MY_HEAD = 3
DANGER = 3
SNAKE_BODY = 4
ENEMY_HEAD = 5
#WALL = 7
directions = ['up', 'left', 'down', 'right']
UP = 0
LEFT = 1
DOWN = 2
RIGHT = 3
# general variables
game_id = ''
board_width = 0
board_height = 0
# my snake variables
direction = 0
health = 100
turn = 0
survival_min = 50
my_id = ''
INITIAL_FEEDING = 3

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

def get_distance(a, b):
    return (abs(a[0] - b[0]) + abs(a[1] - b[1]))

# convert object yx to list yx
def get_coords (o):
    return (o['x'], o['y'])

# return coords to own tail
def get_tail(data):
  body = data['you']['body'][-1]
  return get_coords(body)
    # tail = current_location(data)
    # for segment in body:
    #     tail = get_coords(segment)
    # return tail

# return x,y coords of current head location
def current_location(data):
    return get_coords(data['you']['head'])

# seek closest food
def hungry(data):
    print('HUNGRY! SEEKING FOOD.')
    grid = build_map(data)
    close_food = closest_food(grid, data)
    move = astar(data, grid, close_food, 'food')
    return move

# follow own tail to kill time
def kill_time(data):
    print('COOL. KILLING TIME.')
    grid = build_map(data)
    tail = get_tail(data)
    move = astar(data, grid, tail, 'my_tail')
    return move

def calculate_direction(a, b, grid, data):
    print('CALCULATING NEXT MOVE...')
    x = a[0] - b[0]
    y = a[1] - b[1]
    direction = 0
    # directions = ['up', 'left', 'down', 'right']
    if x < 0:
        direction = 3
    elif x > 0:
        direction = 1
    elif y > 0:
        direction = 2
    count = 0
    if not valid_move(direction, grid, data):
        if count == 3:
            print('DEAD END, NO VALID MOVE REMAINING!')
            print('GAME OVER')
            return direction
        count += 1
        direction += 1
        if direction == 4:
            direction = 0
    return direction

def choose_random(grid, data):
  next_valid = False
  possible_directions = [0, 1, 2, 3]
  while not next_valid:
    print(possible_directions)
    move = random.choice(possible_directions)
    next_valid = valid_move(move, grid, data)
    if not next_valid:
        possible_directions.remove(move)
  return move

def valid_move(d, grid, data):
    global board_height, board_width
    board_height = data["board"]["height"]
    board_width = data["board"]["width"]
    current = current_location(data)
    print("direction: " + str(d) + ' from ' + str(current[0]) + ', ' + str(current[1]))
    print('CHECKING IF MOVE IS VALID!')
    # directions = ['up', 'left', 'down', 'right']
    # check up direction
    if d == 0:
        if current[1] + 1 > board_height - 1:
            print('board_heiigit ' + str(board_height))
            if debug: print('Up move is OFF THE MAP!')
            return False
        if grid[current[0]][current[1] + 1] <= DANGER:
            if debug: print('Up move is VALID.')
            print(str(grid[current[0]][current[1] - 1]))
            return True
        else:
            if debug: print('Up move is FATAL!')
            return False
    #check left direction
    if d == 1:
        if current[0] - 1 < 0:
            if debug: print('Left move is OFF THE MAP!')
            return False
        if grid[current[0] - 1][current[1]] <= DANGER:
            if debug: print('Left move is VALID.')
            return True
        else:
            if debug: print('Left move is FATAL!')
            return False
    # check down direction
    if d == 2:
        if current[1] - 1 < 0:
            if debug: print('Down move is OFF THE MAP!')
            return False
        if grid[current[0]][current[1] - 1] <= DANGER:
            if debug: print('Down move is VALID.')
            return True
        else:
            if debug: print('Down move is FATAL!')
            return False
    # check right direction
    if d == 3:
        if current[0] + 1 > board_width - 1:
            print('board_width ' + str(board_width))
            if debug: print('Right move is OFF THE MAP!')
            return False
        if grid[current[0] + 1][current[1]] <= DANGER:
            if debug: print('Right move is VALID.')
            return True
        else:
            if debug: print('Right move is FATAL!')
            return False
    # failsafe
    if d > 3: print('valid_move FAILED! direction IS NOT ONE OF FOUR POSSIBLE MOVES!')
    return True

# astar pathfinding, from https://github.com/vllry/checkfront-battlesnake
def astar(data, grid, destination, mode):
    print('MAP BUILT! CALCULATING PATH...')
    #destination = get_coords(destination)
    search_scores = build_astar_grid(data, grid)
    open_set = []
    closed_set = []
    # set start location to current head location
    start = current_location(data)
    # on first 3 moves, point to closest food
    if data['turn'] < INITIAL_FEEDING:
        destination = closest_food(grid, data)
    print('astar destination: ' + str(destination))
        # print("astar grid before search:")
        # print_f_scores(search_scores)
    open_set.append(start)
    # while openset is NOT empty keep searching
    while open_set:
        #print("Open set containing ")
        lowest_cell = [9999, 9999] # x, y
        lowest_f = 9999
        # find cell with lowest f score
        for cell in open_set:
            if search_scores[cell[0]][cell[1]].f < lowest_f: # CONSIDER CHANGING TO <= AND THEN ALSO COMPARING G SCORES
                lowest_f = search_scores[cell[0]][cell[1]].f
                lowest_cell = cell
        # found path to destination
        if lowest_cell[0] == destination[0] and lowest_cell[1] == destination[1]:
            print('FOUND A PATH!')
            print("astar grid after search success:")
            # retrace path back to origin to find optimal next move
            temp = lowest_cell
            print('astar start pos: ' + str(start))
            while search_scores[temp[0]][temp[1]].previous[0] != start[0] or search_scores[temp[0]][temp[1]].previous[1] != start[1]:
                temp = search_scores[temp[0]][temp[1]].previous
            # get direction of next optimal move
            print('astar next move: ' + str(temp))
            next_move = calculate_direction(start, temp, grid, data)
            if not valid_move(next_move, grid, data):
                  next_move = choose_random(grid, data)
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
                print('FOUND A PATH! (neighbor)')
                neighbor_cell.previous = current
                print("astar grid after search success:")
                # retrace path back to origin to find optimal next move
                temp = neighbor
                print('astar start pos: ' + str(start))
                while search_scores[temp[0]][temp[1]].previous[0] != start[0] or search_scores[temp[0]][temp[1]].previous[1] != start[1]:
                    temp = search_scores[temp[0]][temp[1]].previous
                # get direction of next optimal move
                print('astar next move: ' + str(temp))
                next_move = calculate_direction(start, temp, grid, data)
                if not valid_move(next_move, grid, data):
                  next_move = choose_random(grid, data)
                return next_move
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
        print('COULD NOT FIND PATH!')
    
        # This is terrible practice but it might work
        move = choose_random(grid, data)

        if mode == 'food':
            tail = get_tail(data)
            move = astar(data, grid, tail, 'my_tail')
        
        return move
        #return best_move(move, data, grid)


# return map array
def build_map(data):
    global my_id, board_height, board_width
    print('BUILDING MAP...')
    my_length = data['you']['length']
    # create map and fill with SPACEs
    grid = [ [SPACE for col in range(data["board"]["width"])] for row in range(data["board"]["width"])]
    turn = data['turn']
    # fill in food locations
    for food in data['board']['food']:
        grid[food['x']][food['y']] = FOOD
    # fill in snake locations
    for snake in data['board']['snakes']:
        for segment in snake['body']:
            # get each segment from data {snakes, data, body, data}
            grid[segment['x']][segment['y']] = SNAKE_BODY
        # mark snake head locations
        #if debug: print('Snake id = ' + str(snake['id']))
        #if debug: print('My id = ' + str(my_id))
        # mark tails as empty spaces only after turn 3
        #if turn > 3:
        if snake['body'][-1] != snake['body'][-2]:
            tempX = snake['body'][-1]['x']
            tempY = snake['body'][-1]['y']
            grid[tempX][tempY] = SPACE
        # dont mark own head or own danger zones
        if snake['id'] == my_id: continue
        head = get_coords(snake['body'][0])
        grid[head[0]][head[1]] = ENEMY_HEAD
        # mark danger locations around enemy head
        # check down from head
        head_zone = DANGER
        if snake['length'] < my_length:
            head_zone = KILL_ZONE
        if (head[1] + 1 < board_height - 1):
            if grid[head[0]][head[1] + 1] < head_zone:
                grid[head[0]][head[1] + 1] = head_zone
        # check up from head
        if (head[1] - 1 > 0):
            if grid[head[0]][head[1] - 1] < head_zone:
                grid[head[0]][head[1] - 1] = head_zone
        # check left from head
        if (head[0] - 1 > 0):
            if grid[head[0] - 1][head[1]] < head_zone:
                grid[head[0] - 1][head[1]] = head_zone
        # check right from head
        if (head[0] + 1 < board_width - 1):
            if grid[head[0] + 1][head[1]] < head_zone:
                grid[head[0] + 1][head[1]] = head_zone
    # mark my head location
    #grid[data['you']['body']['data'][0]['x']][data['you']['body']['data'][0]['y']] = 1
    #if debug: print_map(grid)
    return grid

# return coords of closest food to head, using grid
def closest_food(grid, data):
    my_location = current_location(data)
    close_food = None
    close_distance = 9999
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if grid[i][j] == FOOD:
                food = [i, j]
                distance = get_distance(my_location, food)
                if distance < close_distance:
                    close_food = food
                    close_distance = distance
    return close_food

# return grid of empty Cells for astar search data
def build_astar_grid(data, grid):
    w = data['board']['width']
    h = data['board']['height']
    astar_grid = [ [Cell(row, col) for col in range(h)] for row in range(w)]
    for i in range(w):
        for j in range(h):
            astar_grid[i][j].state = grid[i][j]
    return astar_grid


# the cell class for storing a* search information
class Cell:
    global board_height, board_width
    def __init__(self, x, y):
        self.f = 0
        self.g = 0
        self.h = 0
        self.x = x
        self.y = y
        self.state = 0;
        self.neighbors = []
        self.previous = None
        if self.x < board_width - 1:
            self.neighbors.append([self.x + 1, self.y])
        if self.x > 0:
            self.neighbors.append([self.x - 1, self.y])
        if self.y < board_height - 1:
            self.neighbors.append([self.x, self.y + 1])
        if self.y > 0:
            self.neighbors.append([self.x, self.y - 1])

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

    my_id = data['you']['id']
    health = data['you']['health']
    turn = data['turn']
    survival_min = 21
    # if health is below set threshold
    if health < survival_min:
        taunt = 'Its cool.'
        direction = hungry(data)
    else:
        taunt = 'Super cool.'
        direction = kill_time(data)
    # print data for debugging
    print('REMAINING HEALTH IS ' + str(health) + ' ON TURN ' + str(turn) + '.')
    print('SENDING MOVE: ' + str(directions[direction]))

    return directions[direction]
