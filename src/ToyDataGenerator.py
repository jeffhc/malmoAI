import random
import pprint
import csv

random.seed(5)
width = 3
delay = 3
steps = 5000
world = []

y_offset = 1
for i in range(steps):
    step = [0]
    all_up = True # Helps prevent impossible routes
    for n in range(width):
        up_or_down = random.randint(0,1)
        if up_or_down == 0:
            all_up = False
        if n == (width-1) and all_up:
            up_or_down = 0
        step.append(up_or_down+y_offset)
    if i%delay == 0:
        # Push up base y-value every two steps
        y_offset += 1
    step.append(0)
    world.append(step)

world.append([0]*(width+2))
world.reverse()

# Use filter to create 2x3 situations (called 'frames')

def smallest(sequence):
    """return the minimum nonzero element of sequence"""
    for i in sequence:
        if i != 0:
            low = i # need to start with some value
    for i in sequence:
        if i != 0 and i < low:
            low = i
    return low

frames = []
error_counter = 0
for y in range(steps):
    for x in range(width):
        frame = []
        ## Compress 2x3 frame into a 1-dimensional vector
        #frame.append(world[y][x])
        frame.append(world[y][x+1])
        #frame.append(world[y][x+2])
        frame.append(world[y+1][x])
        frame.append(world[y+1][x+1])
        frame.append(world[y+1][x+2])

        # Make it relative. Lowest nonzero block becomes
        # 1, everything scales down by that. Zeros remain.
        reference_point = smallest(frame) - 1
        if reference_point > 0: # Only get those that need to be relative. (non-early steps)
            _frame = []
            for i in frame:
                if i != 0:
                    _frame.append( i - reference_point )
                else:
                    _frame.append(0)
            frame = _frame

        #### Determine correct answer
        #### Possible answers include: 0-Nothing, 1-Forward, 2-Left, 3-Right, 4-ForwardJump, 5-LeftJump, 6-RightJump
        answer = 0  # Default answer is to do nothing.
        # Check the front
        if frame[0]-frame[2] == 0 or frame[0]-frame[2] == -1: # Prioritize moving forward over elevation
            answer = 1
        elif frame[0]-frame[2] == 1:
            answer = 4
        elif frame[0]-frame[2] == 2:
            # Check left, reached unjumpable forward or divet. TODO: Left has priority over right (arbitrary)
            if frame[1] != 0:
                if frame[1]-frame[2] == 0:
                    answer = 2
                elif frame[1]-frame[2] == 1:
                    answer = 5
                elif frame[1]-frame[2] == -1:
                    # Check right. There's a divet to the left.
                    if frame[3]-frame[2] == 0:
                        answer = 3
                    elif frame[3]-frame[2] == 1:
                        answer = 6
                    elif frame[3]-frame[2] == -1:
                        answer = 3 # Move right anyway
                    else:
                        # Air on right.
                        answer = 2
                else:
                    print("Unknown left case.")
            else:
                # Check right. There's air to the left, and impossible forwards.
                if frame[3]-frame[2] == 0:
                    answer = 3
                elif frame[3]-frame[2] == 1:
                    answer = 6
                elif frame[3]-frame[2] == -1:
                    answer = 3 # Move right anyway
                elif frame[3] == 0:
                    print("Impossible, air on both sides of player.")
                else:
                    print("Unknown right case.")
        else:
            print("Unknown case")

        frame.append(answer)
        if answer != 0: # TODO: Temporary workaround for crappy code.
            frames.append(frame)

#pprint.pprint(world)
#pprint.pprint(frames)

with open("./data.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(frames)

print("DONE")
