from z3 import Bool, Solver, Or, And, Not

environment = [
        [0, 0, 0, 0], 
        [0, 0, 0, 0], 
        [0, 0, 0, 0]]

robot_position = (0, 0)
goal = (2, 3)

obstacles = [(1,1), (1,2)]

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
        if result.get("Up"):
                print("Action: Up")
                for o in obstacles:
                        if o[1] < current[1]:
                                # current[1] = o[1] + 1
                                newPos = (current[0], o[1] + 1)
                                has_obstacle = True
                if not has_obstacle:
                        # current[1] = 0
                        newPos = (current[0], 0)

        elif result.get("Down"):
                print("Action: Down")
                for o in obstacles:
                        if o[1] > current[1]:
                                # current[1] = o[1] - 1
                                newPos = (current[0], o[1] - 1)
                                has_obstacle = True
                if not has_obstacle:
                        # current[1] = len(environment) - 1
                        newPos = (current[0], len(environment) - 1)

        elif result.get("Right"):
                for o in obstacles:
                        if o[0] > current[0]:
                                # current[0] = o[0] - 1
                                newPos = (o[0] - 1, current[1])
                                has_obstacle = True
                if not has_obstacle:
                        # current[0] = len(environment[0]) - 1
                        newPos = (len(environment[0]) - 1, current[1])
        
        elif result.get("Left"):
                for o in obstacles:
                        if o[0] < current[0]:
                                # current[0] = o[0] + 1
                                newPos = (o[0] + 1, current[1])
                                has_obstacle = True
                if not has_obstacle:
                        newPos = (0, current[1])

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

    # Add InitialState Constraint
    # s.add(Not(OnGoal))

    # Add GoalState Constraint
    # s.add(OnGoal)
        
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
        # s.add(BlockedRight == blockedRight(robot_position))
        s.add(TouchingLeft == touchLeft(robot_position))
        s.add(BlockedLeft == blockedLeft(robot_position))
        s.add(OnGoal == (robot_position==goal))


        # TODO: create functions for computing k+1 states
        robot_position_k1 = nextPositon(robot_position, results)
        s.add(BlockedBottomk1 == blockedBottom(robot_position_k1))
        s.add(BlockedLeftk1 == blockedLeft(robot_position_k1))
        s.add(BlockedRightk1 == blockedRight(robot_position_k1))
        s.add(TouchingTopk1 == touchTop(robot_position_k1))
        s.add(TouchingLeftk1 == touchLeft(robot_position_k1))
        s.add(TouchingRightk1 == touchRight(robot_position_k1))
        s.add(OnGoalk1 == (robot_position_k1==goal))

        print(s.check())

        if s.check() == sat:
                results = {
                        "Up": s.model().evaluate(Up),
                        "Down": s.model().evaluate(Down),
                        "Right": s.model().evaluate(Right),
                        "Left": s.model().evaluate(Left)}
                print(results)
                print(results.get("Up"))
                print (nextPositon(robot_position, results))
                robot_position = nextPositon(robot_position, results)

        else:
                print(s.unsat_core())

        # Choose one result

        # TODO: compute the next robot position
        # robot_position = Somthing
        # break

solve()




