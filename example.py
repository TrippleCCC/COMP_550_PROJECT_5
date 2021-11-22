from z3 import *

enviornment = [
        [0, 0, 0, 0], 
        [0, 0, 0, 0], 
        [0, 0, 0, 0],]

robot_position = (0, 0)
goal = (2, 3)

def solve(maxStages = 3):
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

    s = Solver()

    # Add InitialState Constraint
    # s.add(Not(OnGoal))

    # Add GoalState Constraint
    # s.add(OnGoal)
    
    # TODO: exclusion axioms

    while k < maxStages:
        # TODO: Define Frame encodings


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
        s.add(TouchingTop == True)
        s.add(BlockedTop == False)

        # TODO: create functions for computing k+1 states
        s.add(BlockedBottomk1 == False)
        s.add(BlockedLeftk1 == False)
        s.add(BlockedRightk1 == False)
        s.add(TouchingTopk1 == True)
        s.add(TouchingLeftk1 == True)
        s.add(TouchingRightk1 == False)
        s.add(OnGoalk1 == False)


        print(s.check())
        print(type(s.model()))
        results = {
                Up: s.model().evaluate(Up),
                Down: s.model().evaluate(Down),
                Right: s.model().evaluate(Right),
                Left: s.model().evaluate(Left)}
        print(results)

        # Choose one result

        # TODO: compute the next robot position
        robot_position = Somthing
        break
        

solve()
