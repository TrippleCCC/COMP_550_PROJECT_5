from z3 import Bool, Solver, Or, And, Not
import yaml
import argparse

environment = [
        [0, 0, 0, 0], 
        [0, 0, 0, 0], 
        [0, 0, 0, 0]]

robot_position = (0, 0)
goal = (2, 0)

obstacles = [(1,1), (1,2), (1, 0)]

def touchTop(position):
        return position[0] == 0

def touchBottom(position):
        return position[0] == len(environment) - 1

def touchLeft(position):
        return position[1] == 0

def touchRight(position):
        return position[1] == len(environment[0]) - 1

def blockedTop(position):
        for o in obstacles:
                if position[0] == o[0] + 1 and position[1] == o[1]:
                        return True
        return False

def blockedBottom(position):
        for o in obstacles:
                if position[0] == o[0] - 1 and position[1] == o[1]:
                        return True
        return False

def blockedLeft(position):
        for o in obstacles:
                if position[1] == o[1] + 1 and position[0] == o[0]:
                        return True
        return False

def blockedRight(position):
        for o in obstacles:
                if position[1] == o[1] - 1 and position[0] == o[0]:
                        return True
        return False

def nextPositon(current, result):
        newPos = current
        if result.get("Up"):
                print("Action: Up")
                while True:
                    if blockedTop(newPos) or touchTop(newPos):
                        return newPos, "Up"
                    newPos = (newPos[0] - 1, newPos[1])
        elif result.get("Down"):
                print("Action: Down")
                while True:
                    if blockedBottom(newPos) or touchBottom(newPos):
                        return newPos, "Down"
                    newPos = (newPos[0] + 1, newPos[1])
        elif result.get("Right"):
                print("Action: Right")
                while True:
                    if blockedRight(newPos) or touchRight(newPos):
                        return newPos, "Right"
                    newPos = (newPos[0], newPos[1] + 1)
        elif result.get("Left"):
                print("Action: Left")
                while True:
                    if blockedLeft(newPos) or touchLeft(newPos):
                        return newPos, "Left"
                    newPos = (newPos[0], newPos[1] - 1)

        return newPos, None

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
    conjunction = And(conjunction, Or(Not(Up), 
        And(Not(TouchingTop), Not(BlockedTop), BlockedTopk1, BlockedLeftk1, 
            BlockedRightk1, TouchingTopk1, TouchingLeftk1, TouchingRightk1, OnGoalk1)))
    conjunction = And(conjunction, Or(Not(Right), 
        And(Not(TouchingRight), Not(BlockedRight), BlockedTopk1, BlockedBottomk1, 
            BlockedRightk1, TouchingTopk1, TouchingBottom, TouchingRightk1, OnGoalk1)))
    conjunction = And(conjunction, Or(Not(Down), 
        And(Not(TouchingBottom), Not(BlockedBottom), BlockedBottomk1, BlockedLeftk1, 
            BlockedRightk1, TouchingBottomk1, TouchingRightk1, TouchingLeftk1, OnGoalk1)))
    conjunction = And(conjunction, Or(Not(Left), 
        And(Not(TouchingLeft), Not(BlockedLeft), BlockedBottomk1, BlockedLeftk1, 
            BlockedTopk1, TouchingLeftk1, TouchingTopk1, TouchingBottomk1, OnGoalk1)))

    # s.add(Not(And(Up == False, Down == False, Right == False, Left == True)))
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
                "OnGoalk1": s.model().evaluate(OnGoalk1)}

        print(results)

        if results["OnGoal"]:
            print("Solved!")
            break

        robot_position, op = nextPositon(robot_position, results)

        print(robot_position)

        if op == "Up":
            last_move = Down == False
        elif op == "Down":
            last_move = Up == False
        elif op == "Right":
            last_move = Left == False
        elif op == "Left":
            last_move = Right == False
        else:
            last_move = None

        k += 1

        # Choose one result

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

    solve()

