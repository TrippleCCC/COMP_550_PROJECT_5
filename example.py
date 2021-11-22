
from z3 import Bool, Solver, Or, And, Not, sat
# import yaml
import argparse

environment = [
        [0, 0, 0, 0], 
        [0, 0, 0, 0], 
        [0, 0, 0, 0]]

robot_position = (0, 0)
goal = (2, 3)

obstacles = [(0,2), (1,2)]

results = {}
newPos = (0, 0)

def touchTop(position):
        return position[1] == 0

def touchBottom(position):
        return position[1] == len(environment) - 1

def touchLeft(position):
        return position[0] == 0

def touchRight(position):
        return position[0] == len(environment[0]) - 1

def blockedTop(position):
        for o in obstacles:
                if position[1] == o[1] + 1:
                        return True
        return False

def blockedBottom(position):
        for o in obstacles:
                if position[1] == o[1] - 1:
                        return True
        return False

def blockedLeft(position):
        for o in obstacles:
                if position[0] == o[0] + 1:
                        return True
        return False

def blockedRight(position):
        for o in obstacles:
                if position[0] == o[0] - 1:
                        return True
        return False

def nextPositon(current, result):
        has_obstacle = False
        global newPos
        if result.get("Up") == Bool('Up'):
                print("Action: Up")
                for o in obstacles:
                        if o[1] < current[1] and o[0] == current[0]:
                                newPos = (current[0], o[1] + 1)
                                has_obstacle = True
                if not has_obstacle:
                        newPos = (current[0], 0)

        elif result.get("Down") == Bool('Down'):
                print("Action: Down")
                for o in obstacles:
                        if o[1] > current[1] and o[0] == current[0]:
                                newPos = (current[0], o[1] - 1)
                                has_obstacle = True
                if has_obstacle == False:
                        newPos = (current[0], len(environment) - 1)

        elif result.get("Right") == Bool('Right'):
                for o in obstacles:
                        if o[0] > current[0] and o[1] == current[1]:
                                newPos = (o[0] - 1, current[1])
                                has_obstacle = True
                if has_obstacle == False:
                        newPos = (len(environment[0]) - 1, current[1])
                        print(newPos)
        
        elif result.get("Left") == Bool('left'):
                for o in obstacles:
                        if o[0] < current[0]  and o[1] == current[1]:
                                newPos = (o[0] + 1, current[1])
                                has_obstacle = True
                if not has_obstacle:
                        newPos = (0, current[1])

        print(newPos)
        return newPos

def solve(maxStages = 3):
    
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

    InitialState = And(BlockedTop, BlockedLeft, Not(BlockedRight), Not(BlockedBottom), Not(OnGoal))
    
    # Actions
    Up = Bool('Up')
    Right = Bool('Right')
    Down = Bool('Down')
    Left = Bool('Left')

    s = Solver()

#     s.add( And(TouchingTop, TouchingLeft) )

#     s.add( And( TouchingBottom, TouchingRight, onGoal)) 

    # Add InitialState Constraint
#     s.add(Not(OnGoal))

    # Add GoalState Constraint
#     s.add(OnGoal)
        
    # TODO: exclusion axioms
    s.add( Or( Not(Up), Not(Down) ))
    s.add( Or( Not(Up), Not(Right) ))
    s.add( Or( Not(Up), Not(Left) ))
    s.add( Or( Not(Right), Not(Down) ))
    s.add( Or( Not(Right), Not(Left) ))
    s.add( Or( Not(Down), Not(Left) ))


    while k < maxStages:
        # TODO: Define Frame encodings (frame axioms)
        s.add( Or( Up, Not(TouchingTop), TouchingTopk1 ) )
        s.add( Or( Up, Not(BlockedTop), BlockedTopk1 ) ) 
        s.add( Or( Left, Not(TouchingLeft), TouchingLeftk1, Not(BlockedLeft), BlockedLeftk1 ) )
        s.add( Or( Left, Not(BlockedLeft), BlockedLeftk1 ) ) 
        s.add( Or( Down, Not(TouchingBottom), TouchingBottomk1 ) )
        s.add( Or( Down,  Not(BlockedBottom), BlockedBottomk1) )
        s.add( Or( Right, Not(TouchingRight), TouchingRightk1) )
        s.add( Or( Right, Not(BlockedRight), BlockedRightk1 ) )

        s.add( Or( Up, Not(OnGoal), OnGoalk1 ) )
        s.add( Or( Down, Not(OnGoal), OnGoalk1 ) )
        s.add( Or( Right, Not(OnGoal), OnGoalk1 ) )
        s.add( Or( Left, Not(OnGoal), OnGoalk1 ) )

        # Add operator encoding for Up
        s.add(Or(Not(Up), \
            And(Not(TouchingTop), Not(BlockedTop), BlockedTopk1, BlockedLeftk1, \
                BlockedRightk1, TouchingTopk1, TouchingLeftk1, TouchingRightk1, OnGoalk1)))
        s.add(Or(Not(Right), \
            And(Not(TouchingRight), Not(BlockedRight), BlockedTopk1, BlockedBottomk1, \
                BlockedRightk1, TouchingTopk1, TouchingBottom, TouchingRightk1, OnGoalk1)))
        s.add(Or(Not(Down), \
            And(Not(TouchingBottom), Not(BlockedBottom), BlockedBottomk1, BlockedLeftk1, \
                BlockedRightk1, TouchingBottomk1, TouchingRightk1, TouchingLeft, OnGoalk1)))
        s.add(Or(Not(Left), \
            And(Not(TouchingLeft), Not(BlockedLeft), BlockedBottomk1, BlockedLeftk1, \
                BlockedTopk1, TouchingLeftk1, TouchingTopk1, TouchingBottomk1, OnGoalk1)))

        # Add more constrains
        # TODO: create functions for current states
        s.add(TouchingTop == touchTop(robot_position))
        s.add(BlockedTop == blockedTop(robot_position))
        s.add(TouchingBottom == touchBottom(robot_position))
        s.add(BlockedBottom == blockedBottom(robot_position))
        s.add(TouchingRight == touchRight(robot_position))
        s.add(BlockedRight == blockedRight(robot_position))
        s.add(TouchingLeft == touchLeft(robot_position))
        s.add(BlockedLeft == blockedLeft(robot_position))
        s.add(OnGoal == (robot_position==goal))



        print(s.check())

        if s.check() == sat:
                results = {
                        "Up": s.model().evaluate(Up),
                        "Down": s.model().evaluate(Down),
                        "Right": s.model().evaluate(Right),
                        "Left": s.model().evaluate(Left),
                        "TouchingTop": s.model().evaluate(TouchingTop)}
                print(results)
                print (nextPositon(robot_position, results))
                

        else:
                print(s.unsat_core())

        
        # TODO: create functions for computing k+1 states
        robot_position_k1 = nextPositon(robot_position, results)
        s.add(BlockedBottomk1 == blockedBottom(robot_position_k1))
        s.add(BlockedLeftk1 == blockedLeft(robot_position_k1))
        s.add(BlockedRightk1 == blockedRight(robot_position_k1))
        s.add(TouchingTopk1 == touchTop(robot_position_k1))
        s.add(TouchingLeftk1 == touchLeft(robot_position_k1))
        s.add(TouchingRightk1 == touchRight(robot_position_k1))
        s.add(OnGoalk1 == (robot_position_k1==goal))

        # Choose one result
        # results["Right"] = True
        # print(results)


        # TODO: compute the next robot position
        robot_position = nextPositon(robot_position, results)
        # break



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

solve()




