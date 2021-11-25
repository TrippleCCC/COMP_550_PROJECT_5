
from z3 import Bool, Solver, Or, And, Not, sat, Implies
# import yaml
import argparse
import random
import numpy as np

import itertools

import matplotlib.pyplot as plt
from matplotlib import colors
import matplotlib

environment = []
robot_position = (0, 1)
goal = ()
obstacles = [ ]
box = [ ]
stateCounter = {}

def createEnvironment(file):
        global environment
        global goal
        global robot_position
        f = open(file, "r")
        for x in f:
                temp = x.strip().split(' ')
                print(temp[0])
                if temp[0] == 'size':
                        environment = np.ones((int(temp[1]), int(temp[2])))
                if temp[0] == 'g':
                        goal = (int(temp[1]), int(temp[2]))
                if temp[0] == 'r':
                        robot_position = (int(temp[1]), int(temp[2]))
                if temp[0] == 'movable':
                        temp = next(f)
                        while temp != 'obstacle\n':
                                temp1 = temp.strip().split(' ')
                                box.append((int(temp1[0]), int(temp1[1])))
                                temp = next(f)
               
                        temp = next(f)
                        while temp != 'end':
                                temp1 = temp.strip().split(' ')
                                obstacles.append((int(temp1[0]), int(temp1[1])))
                                temp = next(f)
                

def draw(counter, current_position, box_position):

        N1 = len(environment)
        N2 = len(environment[0])
        # make an empty data set
        data = np.ones((N1, N2)) * np.nan
        # fill in some fake data
        for b in box_position:
                data[b[0], b[1]] = 1
        for o in obstacles:
                data[o[0], o[1]] = 0

        data[goal[0], goal[1]] = 2

        data[current_position[0], current_position[1]] = 3

        # make a figure + axes
        fig, ax = plt.subplots(1, 1, tight_layout=True)
        # make color map
        my_cmap = matplotlib.colors.ListedColormap(['k', 'r', 'g', 'b'])
        # set the 'bad' values (nan) to be white and transparent
        my_cmap.set_bad(color='w', alpha=0)
        # draw the grid
        for x in range(N1 + 1):
                for y in range(N2 + 1):
                        ax.axhline(x, lw=2, color='k', zorder=5)
                        ax.axvline(y, lw=2, color='k', zorder=5)
        # draw the boxes
        ax.imshow(data, interpolation='none', cmap=my_cmap, extent=[0, N2, 0, N1], zorder=0)
        # turn off the axis labels
        ax.axis('off')

        plt.savefig('sokoban_' + str(counter) + '.png')


pos_action = []

def touchTop(position):
        return position[0] == 0

def touchBottom(position):
        return position[0] == len(environment) - 1

def touchLeft(position):
        return position[1] == 0

def touchRight(position):
        return position[1] == len(environment[0]) - 1

def blockedTop(position, box):
        for b in box:
                if position[0] == b[0] + 1 and position[1] == b[1] and (blockedTop(b, box) or touchTop(b)):
                        return True

        for o in obstacles:
                if position[0] == o[0] + 1 and position[1] == o[1]:
                        return True
        return False

def blockedBottom(position, box):
        for b in box:
                if position[0] == b[0] - 1 and position[1] == b[1] and (blockedBottom(b, box) or touchBottom(b)):
                        return True
        
        for o in obstacles:
                if position[0] == o[0] - 1 and position[1] == o[1]:
                        return True
        return False

def blockedLeft(position, box):
        for b in box:
                if position[1] == b[1] + 1 and position[0] == b[0] and (blockedLeft(b, box) or touchLeft(b)):
                        return True
        for o in obstacles:
                if position[1] == o[1] + 1 and position[0] == o[0]:
                        return True
        return False

def blockedRight(position, box):

        for b in box:
                if position[1] == b[1] - 1 and position[0] == b[0] and (blockedRight(b, box) or touchRight(b)):
                        print("Blocked by box")
                        return True

        for o in obstacles:
                if position[1] == o[1] - 1 and position[0] == o[0]:
                        return True
        return False


def nextPositon(current, box_position, result):
        newBox = []
        newPos = current

        obs = False

        if result.get("Right"):
                print("Action: Right")

                for b in box_position:

                        for o in obstacles:
                                obs = b[0] == o[0] == newPos[0] and newPos[1] < o[1] < b[1]
                                if obs:
                                        break

                        if not obs:
                                while newPos[0] == b[0] and newPos[1] < b[1] and blockedRight(b, box_position) == False and touchRight(b) == False:
                                        # print("Move box right")
                                        b = (b[0], b[1] + 1)
                        
                        newBox.append(b)
                box_position = newBox

                while True:
                    if blockedRight(newPos, box_position) or touchRight(newPos):
                        return newPos, box_position, "Right"
                    newPos = (newPos[0], newPos[1] + 1)

        elif result.get("Left"):
                print("Action: Left")

                for b in box_position:
                        for o in obstacles:
                                obs = b[0] == o[0] == newPos[0] and newPos[1] > o[1] > b[1]
                                if obs:
                                        break
                        if not obs:
                                while (newPos[0] == b[0] and newPos[1] > b[1] and blockedLeft(b, box_position) == False and touchLeft(b) == False):
                                        b = (b[0], b[1] - 1)
                                # print("Box: " + str(b))
                        newBox.append(b)
                box_position = newBox

                while True:
                    if blockedLeft(newPos, box_position) or touchLeft(newPos):
                        return newPos, box_position, "Left"
                    newPos = (newPos[0], newPos[1] - 1)
        
        elif result.get("Down"):
                print("Action: Down")
                
                for b in box_position:
                        for o in obstacles:
                                obs = b[1] == o[1] == newPos[1] and newPos[0] < o[0] and o[0] < b[0]
                                if obs:
                                        break
                        if (not obs):                
                                while (newPos[1] == b[1] and newPos[0] < b[0] and blockedBottom(b, box_position) == False and touchBottom(b) == False):
                                        b = (b[0] + 1, b[1])
                        
                        newBox.append(b)
                box_position = newBox

                while True:
                    if blockedBottom(newPos, box_position) or touchBottom(newPos):
                        return newPos, box_position, "Down"
                    newPos = (newPos[0] + 1, newPos[1])

        elif result.get("Up"):
                print("Action: Up")
                
                # move the box in the direction of robot
                for b in box_position:
                        for o in obstacles:
                                obs = b[0] == o[0] == newPos[0] and newPos[1] > o[1] > b[1]
                                if obs:
                                        break
                        if not obs:
                                while (newPos[1] == b[1] and newPos[0] > b[0] and blockedTop(b, box_position) == False and touchTop(b) == False):
                                        b = (b[0]-1, b[1])
                        newBox.append(b)
                box_position = newBox

                while True:
                    if blockedTop(newPos, box_position) or touchTop(newPos):
                        return newPos, box_position, "Up"
                    newPos = (newPos[0] - 1, newPos[1])


        return newPos, box_position, None



def solve(current_position, box_position, maxStages):

    k = 0

    print(len(box_position))

    # Define states 
    BlockedTop = Bool('BlockedTop')
    BlockedTopk1 = Bool('BlockedTopk1')
    BlockedLeft = Bool('BlockedLeft')
    BlockedLeftk1 = Bool('BlockedLeftk1')
    BlockedRight = Bool('BlockedRight')
    BlockedRightk1 = Bool('BlockedRightk1')
    BlockedBottom = Bool('BlockedBottom')
    BlockedBottomk1 = Bool('BlockedBottomk1')
    TouchingTop = Bool('TouchingTop')
    TouchingTopk1 = Bool('TouchingTopk1')
    TouchingLeft = Bool('TouchingLeft')
    TouchingLeftk1 = Bool('TouchingLeftk1')
    TouchingRight = Bool('TouchingRight')
    TouchingRightk1 = Bool('TouchingRightk1')
    TouchingBottom = Bool('TouchingBottom')
    TouchingBottomk1 = Bool('TouchingBottomk1')
    OnGoal = Bool('OnGoal')
    OnGoalk1 = Bool('OnGoalk1')

    # Actions
    Up = Bool('Up')
    Right = Bool('Right')
    Down = Bool('Down')
    Left = Bool('Left')
        
    # exclusion axioms

    s = Solver()

    # exclusion axioms,
    conjunction = Or( Not(Up), Not(Down) )
    conjunction = And(conjunction, Or( Not(Up), Not(Right) ))
    conjunction = And(conjunction, Or( Not(Up), Not(Left) ))
    conjunction = And(conjunction, Or( Not(Right), Not(Down) ))
    conjunction = And(conjunction, Or( Not(Right), Not(Left) ))
    conjunction = And(conjunction, Or( Not(Down), Not(Left) ))
   
    # Define Frame encodings (frame axioms)
#     conjunction = And(conjunction, Or( Up, Not(TouchingTop), TouchingTopk1 ) )
#     conjunction = And(conjunction, Or( Up, Right, Left, Not(BlockedTop), BlockedTopk1 ) ) 
#     conjunction = And(conjunction, Or( Left, Not(TouchingLeft), TouchingLeftk1 ))
#     conjunction = And(conjunction, Or( Left, Up, Down, Not(BlockedLeft), BlockedLeftk1 ) ) 
#     conjunction = And(conjunction, Or( Down, Not(TouchingBottom), TouchingBottomk1 ) )
#     conjunction = And(conjunction, Or( Down, Right, Left, Not(BlockedBottom), BlockedBottomk1) )
#     conjunction = And(conjunction, Or( Right, Not(TouchingRight), TouchingRightk1) )
#     conjunction = And(conjunction, Or( Right, Up, Down, Not(BlockedRight), BlockedRightk1 ) )

    conjunction = And(conjunction, Or( Up, Not(OnGoal), OnGoalk1 ) )
    conjunction = And(conjunction, Or( Down, Not(OnGoal), OnGoalk1 ) )
    conjunction = And(conjunction, Or( Right, Not(OnGoal), OnGoalk1 ) )
    conjunction = And(conjunction, Or( Left, Not(OnGoal), OnGoalk1 ) )

#     conjunction = And(conjunction, Or( Up, TouchingTop, Not(TouchingTopk1) ) )
#     conjunction = And(conjunction, Or( Up, Right, Left, BlockedTop, Not(BlockedTopk1) ) ) 
#     conjunction = And(conjunction, Or( Left, TouchingLeft, Not(TouchingLeftk1) ))
#     conjunction = And(conjunction, Or( Left, Up, Down, BlockedLeft, Not(BlockedLeftk1) ) ) 
#     conjunction = And(conjunction, Or( Down, TouchingBottom, Not(TouchingBottomk1) ) )
#     conjunction = And(conjunction, Or( Down, Right, Left, BlockedBottom, Not(BlockedBottomk1)) )
#     conjunction = And(conjunction, Or( Right, TouchingRight, Not(TouchingRightk1)) )
#     conjunction = And(conjunction, Or( Right, Up, Down, BlockedRight, Not(BlockedRightk1) ) )

#     conjunction = And(conjunction, Or( Up, OnGoal, Not(OnGoalk1) ) )
#     conjunction = And(conjunction, Or( Down, OnGoal, Not(OnGoalk1) ) )
#     conjunction = And(conjunction, Or( Right, OnGoal, Not(OnGoalk1) ) )
#     conjunction = And(conjunction, Or( Left, OnGoal, Not(OnGoalk1) ) )


    # Add operator encoding for Up
#     conjunction = And(conjunction, Or(Not(Up), 
#         And(Not(TouchingTop), Not(BlockedTop), BlockedTopk1, BlockedLeftk1, 
#             BlockedRightk1, TouchingTopk1, TouchingLeftk1, TouchingRightk1, OnGoalk1)))

#     conjunction = And(conjunction, Or(Not(Right), 
#         And(Not(TouchingRight), Not(BlockedRight), BlockedTopk1, BlockedBottomk1, 
#             BlockedRightk1, TouchingTopk1, TouchingBottom, TouchingRightk1, OnGoalk1)))

#     conjunction = And(conjunction, Or(Not(Down), 
#         And(Not(TouchingBottom), Not(BlockedBottom), BlockedBottomk1, BlockedLeftk1, 
#             BlockedRightk1, TouchingBottomk1)))

#     conjunction = And(conjunction, Or(Not(Left), 
#         And(Not(TouchingLeft), Not(BlockedLeft), BlockedBottomk1, BlockedLeftk1, 
#             BlockedTopk1, TouchingLeftk1, TouchingTopk1, TouchingBottomk1, OnGoalk1)))

    conjunction = And(conjunction, Or(Not(Up), 
        And(Not(TouchingTop), Not(BlockedTop), BlockedTopk1, TouchingTopk1)))

    conjunction = And(conjunction, Or(Not(Right), 
        And(Not(TouchingRight), Not(BlockedRight), BlockedRightk1, TouchingRightk1)))

    conjunction = And(conjunction, Or(Not(Down), 
        And(Not(TouchingBottom), Not(BlockedBottom), BlockedBottomk1, TouchingBottomk1)))

    conjunction = And(conjunction, Or(Not(Left), 
        And(Not(TouchingLeft), Not(BlockedLeft),  BlockedLeftk1,  TouchingLeftk1)))

#     s.add(Not(And(Up == True, Down == False, Right == False, Left == False)))
    s.add(Not(conjunction))

    last_move = None

    while k < maxStages - 1:

        # Add more constrains
        s.add(Not(And(Up == False, Down == False, Right == False, Left == False)))
        s.add(Not(conjunction))
        s.add(TouchingTop == touchTop(current_position))
        s.add(BlockedTop == blockedTop(current_position, box_position))
        s.add(TouchingBottom == touchBottom(current_position))
        s.add(BlockedBottom == blockedBottom(current_position, box_position))
        s.add(TouchingRight == touchRight(current_position))
        s.add(BlockedRight == blockedRight(current_position, box_position))
        s.add(TouchingLeft == touchLeft(current_position))
        s.add(BlockedLeft == blockedLeft(current_position, box_position))
        s.add(OnGoal == (current_position==goal))


        if last_move is not None:
            s.add(last_move)

        # print(s)
        if str(s.check()) != "sat":
            break

        results = {
                "Up": s.model().evaluate(Up),
                "Down": s.model().evaluate(Down),
                "Right": s.model().evaluate(Right),
                "Left": s.model().evaluate(Left),
                "OnGoal": s.model().evaluate(OnGoal),
                "OnGoalk1": s.model().evaluate(OnGoalk1)
                # "TouchingTop": s.model().evaluate(TouchingTop),
                # "TouchingTopk1": s.model().evaluate(TouchingTopk1),
                # "BlockedTop": s.model().evaluate(BlockedTop),
                # "BlockedTopk1": s.model().evaluate(BlockedTopk1),
                # "TouchingBottom": s.model().evaluate(TouchingBottom),
                # "TouchingBottomk1": s.model().evaluate(TouchingBottomk1),
                # "BlockedBottom": s.model().evaluate(BlockedBottom),
                # "BlockedBottomk1": s.model().evaluate(BlockedBottomk1)
                }

        print(results)
        print(box_position)

        if results["OnGoal"]:
            print("Solved!")
            break

        # if the position has two possible actions, and already took the first action
        # choose the next available action
        actions = []
        if results.get("Up"):
                actions.append("Up")
        if results.get("Down"):
                actions.append("Down")
        if results.get("Right"):
                actions.append("Right")
        if results.get("Left"):
                actions.append("Left")
        
        
        # # print(actions)
        # if robot_position in pos_action.keys():
        #         if len(pos_action[robot_position]) > 1:
        #                 print("More than 1 action")
        #                 temp = pos_action[robot_position]
                        
        #                 # use the next available action
        #                 results[temp[0]] = False
        #                 temp.pop(0)

        # else:
        #         pos_action[robot_position] = actions
        #         # print(pos_action[robot_position])
                
        state_position = box_position
        state_position.append(current_position)

        
        if len(actions) > 1:
                # randomly choose an action


                        # index = random.randint(0, len(actions) - 1)
                        # results[actions[index]] = True

                        for a in actions:
                                list_cycle = itertools.cycle(actions)

                                if state_position in pos_action:
                                        a = next(list_cycle)
                                else:
                                        pos_action.append(state_position)

                                results["Up"] = False
                                results["Down"] = False
                                results["Left"] = False
                                results["Right"] = False

                                results[a] = True

                                print("Before nextPosition() " + str(len(box_position)))
                                current_position, box_position, op = nextPositon(current_position, box_position, results)
                                print("After nextPosition() " + str(len(box_position)))

                                print("Current: " + str(current_position))
                                print("Box: " + str(box_position))
                                draw(k, current_position, box_position)
                                
                                if op == "Up":
                                        last_move = And(Down == False, Up == False)
                                elif op == "Down":
                                        last_move = And(Up == False, Down == False)
                                elif op == "Right":
                                        last_move = Left == False
                                elif op == "Left":
                                        last_move = Right == False
                                else:
                                        last_move = None

                                k += 1

                                print("Getting deeper")
                                solve(current_position, box_position, 25-k)

  

        current_position, box_position, op = nextPositon(current_position, box_position, results)

        print(current_position)
        draw(k, current_position, box_position)

        if op == "Up":
            last_move = And(Down == False, Up == False)
        elif op == "Down":
            last_move = And(Up == False, Down == False)
        elif op == "Right":
            last_move = Left == False
        elif op == "Left":
            last_move = Right == False
        else:
            last_move = None

        k += 1

        s.reset()



def readEnviornment(filename):
    robotStart = None
    robotGoal = None
    envDimimensions = None
    obstacles = []
    with open(filename) as file:
        envYaml = yaml.full_load(file)

        if envYaml:
            envDimimensions = (envYaml["dimensions"]["width"], envYaml["dimensions"]["height"])

            robotStart = (envYaml["robot_start"]["x"], envYaml["robot_start"]["y"])
            robotGoal = (envYaml["robot_goal"]["x"], envYaml["robot_goal"]["y"])

            for _, coord in envYaml["obstacles"].items():
                obstacles.append((coord["x"], coord["y"]))


    return envDimimensions, robotStart, robotGoal, obstacles

# Define command line arguments
parser = argparse.ArgumentParser(description="Sokoban on Ice solver.")
parser.add_argument("--env", help="yaml file describing the input environment")

if __name__ == "__main__":
    # TODO: read in environment

    args = vars(parser.parse_args())

    envFile = args["env"]

    if envFile:
        envDimimensions, robotStart, robotGoal, obstacles = readEnviornment(envFile)
        print(envDimimensions, robotStart, robotGoal, obstacles)
    else:
        # TODO: implement default environment
        print("Using default environment...")


# draw()
createEnvironment("scene2")
solve(robot_position, box, 25)

