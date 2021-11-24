
from z3 import Bool, Solver, Or, And, Not, sat, Implies
# import yaml
import argparse
import random
import numpy as np

import matplotlib.pyplot as plt
from matplotlib import colors
import matplotlib

# environment = [
#         [0, 0, 0], 
#         [0, 0, 0], 
#         [0, 0, 0]]

# environment = [
#         [0, 0, 0, 0], 
#         [0, 0, 0, 0], 
#         [0, 0, 0, 0]]

# environment = [
#         [0, 0, 0, 0], 
#         [0, 0, 0, 0], 
#         [0, 0, 0, 0],
#         [0, 0, 0, 0]]

# environment = [
#         [0, 0, 0, 0, 0, 0, 0, 0], 
#         [0, 0, 0, 0, 0, 0, 0, 0], 
#         [0, 0, 0, 0, 0, 0, 0, 0],
#         [0, 0, 0, 0, 0, 0, 0, 0]]

# environment = [
#         [0, 0, 0, 0, 0, 0], 
#         [0, 0, 0, 0, 0, 0],
#         [0, 0, 0, 0, 0, 0],
#         [0, 0, 0, 0, 0, 0],
#         [0, 0, 0, 0, 0, 0],
#         [0, 0, 0, 0, 0, 0]]
environment = []

# robot_position = (3, 0)
# robot_position = (0, 0)
robot_position = (0, 1)
# goal = (2, 2)
# goal = (2, 0)
# goal = (1, 7)
# goal = (3, 1)
# goal = (4, 3)
goal = ()

# obstacles = [(1, 0), (1, 1), (1, 2)]
# obstacles = [(1,1), (1,2), (1, 0)]
# obstacles = [(3, 0), (1, 0), (1, 1), (2, 2),  (0, 3)]

# obstacles = [(3, 1), (0, 2), (3, 4), (2, 6)]

# obstacles = [(1, 0)]
# box = [(1, 1), (0, 2)]

# obstacles = [(0, 0), (0, 3), (2, 2), (2, 5), (4, 1), (5, 2)]
# box = [(1, 1), (1, 4), (3, 4), (5, 4)]

obstacles = [ ]
box = [ ]

def createEnvironment(file):
        global environment
        global goal
        global robot_position
        f = open(file, "r")
        for x in f:
                temp = x.strip().split(' ')
                print(temp[0])
                if temp[0] == 'size':
                        print("size")
                        environment = np.ones((int(temp[1]), int(temp[2])))
                if temp[0] == 'g':
                        goal = (int(temp[1]), int(temp[2]))
                if temp[0] == 'r':
                        robot_position = (int(temp[1]), int(temp[2]))
                if temp[0] == 'movable':
                        print("Moveable")
                        temp = next(f)
                        while temp != 'obstacle\n':
                                print(temp)
                                temp1 = temp.strip().split(' ')
                                box.append((int(temp1[0]), int(temp1[1])))
                                temp = next(f)
               
                        print("Obstacle")
                        temp = next(f)
                        while temp != 'end':
                                print(temp)
                                temp1 = temp.strip().split(' ')
                                obstacles.append((int(temp1[0]), int(temp1[1])))
                                temp = next(f)
        print(obstacles)
        print(box)

                

def draw(counter):

        N1 = len(environment)
        N2 = len(environment[0])
        # make an empty data set
        data = np.ones((N1, N2)) * np.nan
        # fill in some fake data
        for b in box:
                data[b[0], b[1]] = 1
        for o in obstacles:
                data[o[0], o[1]] = 0

        data[goal[0], goal[1]] = 2

        data[robot_position[0], robot_position[1]] = 3

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

# if boxes are moved to corners, they become obstacles
def boxToObs ():
        global box
        for b in box:
                if(b == (0, 0) or b == (0, len(environment[0])-1) or b == (len(environment)-1, 0) or b == (len(environment), len(environment[0])-1)):
                        box.remove(b)
                        obstacles.append(b)

pos_action = {}

def touchTop(position):
        return position[0] == 0

def touchBottom(position):
        return position[0] == len(environment) - 1

def touchLeft(position):
        return position[1] == 0

def touchRight(position):
        return position[1] == len(environment[0]) - 1

def blockedTop(position):
        for b in box:
                if position[0] == b[0] + 1 and position[1] == b[1] and (blockedTop(b) or touchTop(b)):
                        return True

        for o in obstacles:
                if position[0] == o[0] + 1 and position[1] == o[1]:
                        return True
        return False

def blockedBottom(position):
        for b in box:
                if position[0] == b[0] - 1 and position[1] == b[1] and (blockedBottom(b) or touchBottom(b)):
                        return True
        
        for o in obstacles:
                if position[0] == o[0] - 1 and position[1] == o[1]:
                        return True
        return False

def blockedLeft(position):
        for b in box:
                if position[1] == b[1] + 1 and position[0] == b[0] and (blockedLeft(b) or touchLeft(b)):
                        return True
        for o in obstacles:
                if position[1] == o[1] + 1 and position[0] == o[0]:
                        return True
        return False

def blockedRight(position):

        for b in box:
                if position[1] == b[1] - 1 and position[0] == b[0] and (blockedRight(b) or touchRight(b)):
                        print("Blocked by box")
                        return True

        for o in obstacles:
                if position[1] == o[1] - 1 and position[0] == o[0]:
                        return True
        return False


def nextPositon(current, result):
        global box
        newBox = []
        newPos = current
        if result.get("Right"):
                print("Action: Right")

                for b in box:

                        for o in obstacles:
                                if not(b[0] == o[0] == newPos[0] and newPos[1] < o[1] < b[1]):

                                        while newPos[0] == b[0] and newPos[1] < b[1] and blockedRight(b) == False and touchRight(b) == False:
                                                # print("Move box right")
                                                b = (b[0], b[1] + 1)
                        newBox.append(b)
                box = newBox

                while True:
                    if blockedRight(newPos) or touchRight(newPos):
                        return newPos, "Right"
                    newPos = (newPos[0], newPos[1] + 1)

        elif result.get("Left"):
                print("Action: Left")

                for b in box:
                        for o in obstacles:
                                if not(b[0] == o[0] == newPos[0] and newPos[1] > o[1] > b[1]):
                                        while (newPos[0] == b[0] and newPos[1] > b[1] and blockedLeft(b) == False and touchLeft(b) == False):
                                                b = (b[0], b[1] - 1)
                                # print("Box: " + str(b))
                        newBox.append(b)
                box = newBox

                while True:
                    if blockedLeft(newPos) or touchLeft(newPos):
                        return newPos, "Left"
                    newPos = (newPos[0], newPos[1] - 1)
        
        elif result.get("Down"):
                print("Action: Down")
                
                for b in box:
                        for o in obstacles:
                                if not(b[1] == o[1] == newPos[1] and newPos[0] < o[0] < b[0]):
                                        while (newPos[1] == b[1] and newPos[0] < b[0] and blockedBottom(b) == False and touchBottom(b) == False):
                                                b = (b[0] + 1, b[1])
                        newBox.append(b)
                box = newBox

                while True:
                    if blockedBottom(newPos) or touchBottom(newPos):
                        return newPos, "Down"
                    newPos = (newPos[0] + 1, newPos[1])

        elif result.get("Up"):
                print("Action: Up")
                
                # move the box in the direction of robot
                for b in box:
                        for o in obstacles:
                                if not(b[0] == o[0] == newPos[0] and newPos[1] > o[1] > b[1]):
                                        while (newPos[1] == b[1] and newPos[0] > b[0] and blockedTop(b) == False and touchTop(b) == False):
                                                b = (b[0]-1, b[1])
                        newBox.append(b)
                box = newBox

                while True:
                    if blockedTop(newPos) or touchTop(newPos):
                        return newPos, "Up"
                    newPos = (newPos[0] - 1, newPos[1])


        return newPos, None


def solve(maxStages = 25):
    
    global robot_position

    k = 0

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
        s.add(TouchingTop == touchTop(robot_position))
        s.add(BlockedTop == blockedTop(robot_position))
        s.add(TouchingBottom == touchBottom(robot_position))
        s.add(BlockedBottom == blockedBottom(robot_position))
        s.add(TouchingRight == touchRight(robot_position))
        s.add(BlockedRight == blockedRight(robot_position))
        s.add(TouchingLeft == touchLeft(robot_position))
        s.add(BlockedLeft == blockedLeft(robot_position))
        s.add(OnGoal == (robot_position==goal))

        # s.add(Not(TouchingTop == touchTop(robot_position)))
        # s.add(Not(BlockedTop == blockedTop(robot_position)))
        # s.add(Not(TouchingBottom == touchBottom(robot_position)))
        # s.add(Not(BlockedBottom == blockedBottom(robot_position)))
        # s.add(Not(TouchingRight == touchRight(robot_position)))
        # s.add(Not(BlockedRight == blockedRight(robot_position)))
        # s.add(Not(TouchingLeft == touchLeft(robot_position)))
        # s.add(Not(BlockedLeft == blockedLeft(robot_position)))
        # s.add(Not(OnGoal == (robot_position==goal)))

        # s.add(Not(And(Not(Down), TouchingBottom)))

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
        print(box)

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
                        
        #                 # # use the next available action
        #                 # results[temp[0]] = False
        #                 # temp.pop(0)

        # else:
        #         pos_action[robot_position] = actions
        #         # print(pos_action[robot_position])
                
        if len(actions) > 1:
                # randomly choose an action
                        print("More than one action")
                        results["Up"] = False
                        results["Down"] = False
                        results["Left"] = False
                        results["Right"] = False

                        index = random.randint(0, len(actions) - 1)
                        results[actions[index]] = True
  


        robot_position, op = nextPositon(robot_position, results)

        print(robot_position)
        draw(k)

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

        # Choose one result
        # results["Right"] = True
        # print(results)

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
createEnvironment("scene1")
solve()

