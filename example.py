
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
        if result.get("Up") == Bool("Up"):
                print("Action: Up")
                for o in obstacles:
                        if o[1] < current[1] and o[0] == current[0]:
                                newPos = (current[0], o[1] + 1)
                                has_obstacle = True
                if not has_obstacle:
                        newPos = (current[0], 0)

        elif result.get("Down") == bool("Down"):
                print("Action: Down")
                for o in obstacles:
                        if o[1] > current[1] and o[0] == current[0]:
                                newPos = (current[0], o[1] - 1)
                                has_obstacle = True
                if has_obstacle == False:
                        newPos = (current[0], len(environment) - 1)

        elif result.get("Right") == bool("Right") :
                print("Action: Right")
                for o in obstacles:
                        if o[0] > current[0] and o[1] == current[1]:
                                newPos = (o[0] - 1, current[1])
                                has_obstacle = True
                if has_obstacle == False:
                        newPos = (len(environment[0]) - 1, current[1])
                        print(newPos)
        
        elif result.get("Left") ==  bool("Left"):
                print("Action: Left")
                for o in obstacles:
                        if o[0] < current[0]  and o[1] == current[1]:
                                newPos = (o[0] + 1, current[1])
                                has_obstacle = True
                if not has_obstacle:
                        newPos = (0, current[1])

        print(newPos)
        return newPos

def solve(maxStages = 5):
    
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

    # s = Solver()

    # InitialState = And(BlockedBottom, BlockedLeft, Not(BlockedRight), Not(BlockedTop), Not(OnGoal))
    # GoalState = And(BlockedTop, BlockedRight, Not(BlockedLeft), Not(BlockedBottom), OnGoal)

#     s.add( And(TouchingTop, TouchingLeft) )

#     s.add( And( TouchingBottom, TouchingRight, onGoal)) 

    # Add InitialState Constraint
    # s.add(InitialState)

    # Add GoalState Constraint
    # s.add(GoalState)
        
    # exclusion axioms
    # s.add( Or( Not(Up), Not(Down) ))
    # s.add( Or( Not(Up), Not(Right) ))
    # s.add( Or( Not(Up), Not(Left) ))
    # s.add( Or( Not(Right), Not(Down) ))
    # s.add( Or( Not(Right), Not(Left) ))
    # s.add( Or( Not(Down), Not(Left) ))

    s = Solver()

    while k < maxStages:
        
        conjunction = True
        # exclusion axioms,
        conjunction = And(conjunction, Or( Not(Up), Not(Down) ))
        conjunction = And(conjunction, Or( Not(Up), Not(Right) ))
        conjunction = And(conjunction, Or( Not(Up), Not(Left) ))
        conjunction = And(conjunction, Or( Not(Right), Not(Down) ))
        conjunction = And(conjunction, Or( Not(Right), Not(Left) ))
        conjunction = And(conjunction, Or( Not(Down), Not(Left) ))
        # Define Frame encodings (frame axioms)
        conjunction = And(conjunction, Or( Up, Not(TouchingTop), TouchingTopk1 ) )
        conjunction = And(conjunction, Or( Up, Right, Left, Not(BlockedTop), BlockedTopk1 ) ) 
        conjunction = And(conjunction, Or( Left, Not(TouchingLeft), TouchingLeftk1 ))
        conjunction = And(conjunction, Or( Left, Up, Down, Not(BlockedLeft), BlockedLeftk1 ) ) 
        conjunction = And(conjunction, Or( Down, Not(TouchingBottom), TouchingBottomk1 ) )
        conjunction = And(conjunction, Or( Down, Right, Left, Not(BlockedBottom), BlockedBottomk1) )
        conjunction = And(conjunction, Or( Right, Not(TouchingRight), TouchingRightk1) )
        conjunction = And(conjunction, Or( Right, Up, Down, Not(BlockedRight), BlockedRightk1 ) )

        conjunction = And(conjunction, Or( Up, Not(OnGoal), OnGoalk1 ) )
        conjunction = And(conjunction, Or( Down, Not(OnGoal), OnGoalk1 ) )
        conjunction = And(conjunction, Or( Right, Not(OnGoal), OnGoalk1 ) )
        conjunction = And(conjunction, Or( Left, Not(OnGoal), OnGoalk1 ) )

        # Add operator encoding for Up
        conjunction = And(conjunction,Or(Not(Up), \
            And(Not(TouchingTop), Not(BlockedTop), BlockedTopk1, BlockedLeftk1, \
                BlockedRightk1, TouchingTopk1, TouchingLeftk1, TouchingRightk1, OnGoalk1)))
        conjunction = And(conjunction,Or(Not(Right), \
            And(Not(TouchingRight), Not(BlockedRight), BlockedTopk1, BlockedBottomk1, \
                BlockedRightk1, TouchingTopk1, TouchingBottom, TouchingRightk1, OnGoalk1)))
        conjunction = And(conjunction,Or(Not(Down), \
            And(Not(TouchingBottom), Not(BlockedBottom), BlockedBottomk1, BlockedLeftk1, \
                BlockedRightk1, TouchingBottomk1, TouchingRightk1, TouchingLeft, OnGoalk1)))
        conjunction = And(conjunction,Or(Not(Left), \
            And(Not(TouchingLeft), Not(BlockedLeft), BlockedBottomk1, BlockedLeftk1, \
                BlockedTopk1, TouchingLeftk1, TouchingTopk1, TouchingBottomk1, OnGoalk1)))

        # Add more constrains
        # TODO: create functions for current states
        # s.add(TouchingTop == touchTop(robot_position))
        # s.add(BlockedTop == blockedTop(robot_position))
        # s.add(TouchingBottom == touchBottom(robot_position))
        # s.add(BlockedBottom == blockedBottom(robot_position))
        # s.add(TouchingRight == touchRight(robot_position))
        # s.add(BlockedRight == blockedRight(robot_position))
        # s.add(TouchingLeft == touchLeft(robot_position))
        # s.add(BlockedLeft == blockedLeft(robot_position))
        # s.add(OnGoal == (robot_position==goal))
        # print("Conjuection: " + str(conjunction))
        conjunction = And(conjunction,TouchingTop == touchTop(robot_position))
        print("Touching Top: " + str(touchTop(robot_position)))
        conjunction = And(conjunction,BlockedTop == blockedTop(robot_position))
        conjunction = And(conjunction,TouchingBottom == touchBottom(robot_position))
        conjunction = And(conjunction,BlockedBottom == blockedBottom(robot_position))
        conjunction = And(conjunction,TouchingRight == touchRight(robot_position))
        conjunction = And(conjunction,BlockedRight == blockedRight(robot_position))
        conjunction = And(conjunction,TouchingLeft == touchLeft(robot_position))
        conjunction = And(conjunction,BlockedLeft == blockedLeft(robot_position))
        conjunction = And(conjunction,OnGoal == (robot_position==goal))

        s.add(Not(conjunction))
        # s.add(Not(And(Up == False, Right == False, Left == False, Down == False)))


        print(s.check())
        
        # TODO: create functions for computing k+1 states

        # results = {}
        # robot_position_k1 = nextPositon(robot_position, results)
        # s.add(BlockedBottomk1 == blockedBottom(robot_position_k1))
        # s.add(BlockedLeftk1 == blockedLeft(robot_position_k1))
        # s.add(BlockedRightk1 == blockedRight(robot_position_k1))
        # s.add(TouchingTopk1 == touchTop(robot_position_k1))
        # s.add(TouchingLeftk1 == touchLeft(robot_position_k1))
        # s.add(TouchingRightk1 == touchRight(robot_position_k1))
        # s.add(OnGoalk1 == (robot_position_k1==goal))

        print(s.check())

        # if s.check() == "sat":
        results = {
                "Up": s.model().evaluate(Up),
                "Down": s.model().evaluate(Down),
                "Right": s.model().evaluate(Right),
                "Left": s.model().evaluate(Left),
                "TouchingTop": s.model().evaluate(TouchingTop),
                "TouchingBottom": s.model().evaluate(TouchingBottom),
                # "TouchingLeft": s.model().evaluate(TouchingLeft),
                # "TouchingRight": s.model().evaluate(TouchingRight),
                "BlockedTop": s.model().evaluate(BlockedTop),
                "TouchingTopk1": s.model().evaluate(TouchingTopk1),}
        print(results, touchTop(robot_position), touchBottom(robot_position))
        # print(results.get("Up"))
        # print (nextPositon(robot_position, results))
                

        # else:
        # print(s.unsat_core())

        k += 1

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




