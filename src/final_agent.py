from __future__ import print_function
from __future__ import division

# Practicing how to build a world using the XML API.

from builtins import range
from past.utils import old_div
import MalmoPython
import os
import sys
import time
import random
import json
import pprint
from keras.models import Sequential
from keras.layers import Dense
from keras.models import model_from_json
import numpy as np

if sys.version_info[0] == 2:
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)  # flush print output immediately
else:
    import functools
    print = functools.partial(print, flush=True)

# Seed 5 is original
# For slope of 1, seed 7 gets us in infinite loop.
# Seed 25, slope 1 modified can be completed perfectly.
random.seed(5)

def Moguls(steps, delay, width, starting_x, starting_y, starting_z):
    genstring = "\n"
    y_offset = 0
    for i in range(steps):
        all_up = True # Helps prevent impossibly routes
        for n in range(width):
            up_or_down = random.randint(0,1)
            if up_or_down == 0:
                all_up = False
            if n == (width-1) and all_up:
                up_or_down = 0
            genstring += '<DrawBlock x="%d" y="%d" z="%d" type="grass"/>\n' % (i+starting_x, up_or_down+y_offset+starting_y, n+starting_z)
            # NOTE: ALLOW FRAME COUNTER TO WORK AND Fill in ugly holes
            genstring += '<DrawBlock x="%d" y="%d" z="%d" type="dirt"/>\n' % (i+starting_x, up_or_down+y_offset+starting_y-1, n+starting_z)
            genstring += '<DrawBlock x="%d" y="%d" z="%d" type="dirt"/>\n' % (i+starting_x, up_or_down+y_offset+starting_y-2, n+starting_z)
            genstring += '<DrawBlock x="%d" y="%d" z="%d" type="dirt"/>\n' % (i+starting_x, up_or_down+y_offset+starting_y-3, n+starting_z)
        if i%delay == 0:
            # Push up base y-value every two steps
            y_offset += 1
    return genstring


missionXML='''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
            <Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">

              <About>
                <Summary>Staircase to Heaven!</Summary>
              </About>

            <ServerSection>
              <ServerInitialConditions>
                <Time>
                    <StartTime>1000</StartTime>
                    <AllowPassageOfTime>false</AllowPassageOfTime>
                </Time>
                <Weather>clear</Weather>
              </ServerInitialConditions>
              <ServerHandlers>
                  <FlatWorldGenerator generatorString="3;7,1,24;1;"/>
                  <DrawingDecorator>
                    <DrawBlock x="0" y="2" z="0" type="diamond_block"/>''' + Moguls(50, 3, 3, 2, 2, -1) + Moguls(50, 2, 3, 2, 2, 3) + Moguls(50, 1, 3, 2, 2, 7) +'''</DrawingDecorator>
                  <ServerQuitFromTimeUp timeLimitMs="30000"/>
                  <ServerQuitWhenAnyAgentFinishes/>
                </ServerHandlers>
              </ServerSection>

              <AgentSection mode="Survival">
                <Name>MalmoTutorialBot</Name>
                <AgentStart>
                    <Placement x="0.5" y="3" z="0.5" yaw="-90"/>
                    <Inventory>
                        <InventoryItem slot="8" type="diamond_pickaxe"/>
                        <InventoryItem slot="7" type="stone" quantity="64"/>
                    </Inventory>
                </AgentStart>
                <AgentHandlers>
                  <ObservationFromFullStats/>
                  <ObservationFromGrid>
                      <Grid name="floor1">
                        <min x="-1" y="-2" z="-1"/>
                        <max x="1" y="-2" z="1"/>
                      </Grid>
                      <Grid name="floor2">
                        <min x="-1" y="-1" z="-1"/>
                        <max x="1" y="-1" z="1"/>
                      </Grid>
                      <Grid name="floor3">
                        <min x="-1" y="0" z="-1"/>
                        <max x="1" y="0" z="1"/>
                      </Grid>
                      <Grid name="floor4">
                        <min x="-1" y="1" z="-1"/>
                        <max x="1" y="1" z="1"/>
                      </Grid>
                  </ObservationFromGrid>
                    <DiscreteMovementCommands/>
                  <InventoryCommands/>
                  <AgentQuitFromReachingPosition>
                    <Marker x="-26.5" y="40.0" z="0.5" tolerance="0.5" description="Goal_found"/>
                  </AgentQuitFromReachingPosition>
                </AgentHandlers>
              </AgentSection>
            </Mission>'''

# Create default Malmo objects:

#print(Menger(-40, 40, -13, 27, "stone", "smooth_granite", "air"))

agent_host = MalmoPython.AgentHost()
try:
    agent_host.parse( sys.argv )
except RuntimeError as e:
    print('ERROR:',e)
    print(agent_host.getUsage())
    exit(1)
if agent_host.receivedArgument("help"):
    print(agent_host.getUsage())
    exit(0)

my_mission = MalmoPython.MissionSpec(missionXML, True)
my_mission_record = MalmoPython.MissionRecordSpec()
my_mission.allowAllDiscreteMovementCommands()

# Attempt to start a mission:
max_retries = 3
for retry in range(max_retries):
    try:
        agent_host.startMission( my_mission, my_mission_record )
        break
    except RuntimeError as e:
        if retry == max_retries - 1:
            print("Error starting mission:",e)
            exit(1)
        else:
            time.sleep(2)

# Loop until mission starts:
print("Waiting for the mission to start ", end=' ')
world_state = agent_host.getWorldState()
while not world_state.has_mission_begun:
    print(".", end="")
    time.sleep(0.1)
    world_state = agent_host.getWorldState()
    for error in world_state.errors:
        print("Error:",error.text)

print()
print("Mission running ", end=' ')

### START OF AGENT CODE

def between(a, x, b):
    if x > a and x < b:
        return True
    else:
        return False

def smallest(sequence):
    """return the minimum nonzero element of sequence"""
    for i in sequence:
        if i != 0:
            low = i # need to start with some value
    for i in sequence:
        if i != 0 and i < low:
            low = i
    return low

def filterGrid(a, b, c, d, master_grid):
    new_master_grid = []
    for grid in master_grid:
        _grid = []
        _grid.append(grid[a])
        _grid.append(grid[b])
        _grid.append(grid[c])
        _grid.append(grid[d])
        new_master_grid.append(_grid)
    # new_master_grid.reverse()         # WHICH LAYER DO YOU WANT TO SHOW ON TOP?
    return new_master_grid

def get_state(grid1, grid2, grid3, grid4, yaw):
    direction = None
    if between(135, yaw, 225) or between(-225, yaw, -135):
        direction = "north"
    elif between(45, yaw, 135) or between(-315, yaw, -225):
        direction = "west"
    elif between(225, yaw, 315) or between(-135, yaw, -45):
        direction = "east"
    elif (between(0, yaw, 45) or between(315, yaw, 360)) or (between(-45, yaw, 0) or between(-360, yaw, -315)):
        direction = "south"
    else:
        print("UNKNOWN DIRECTION")
    #print(direction)

    master_grid = [grid1, grid2, grid3, grid4]
    state = []
    if direction == "north":
        state = filterGrid(1, 3, 4, 5, master_grid)
    elif direction == "west":
        state = filterGrid(3, 7, 4, 1, master_grid)
    elif direction == "east":
        state = filterGrid(5, 1, 4, 7, master_grid)
    elif direction == "south":
        state = filterGrid(7, 5, 4, 3, master_grid)
    else:
        print("No direction")

    frame = [0, 0, 0, 0]
    for layer in state:
        for index, block in enumerate(layer):
            if block != "air":
                frame[index] += 1

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

    return direction, frame


#### Initialize Keras network
# load json and create model
json_file = open('model.json', 'r')
loaded_model_json = json_file.read()
json_file.close()
loaded_model = model_from_json(loaded_model_json)
# load weights into new model
loaded_model.load_weights("model.h5")
print("Loaded model from disk")
loaded_model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])


def move(x, y, z, direction, action):
    # TODO: DIRECTIONS ARE ALL SCREWED UP
    if action == 0:
        print("Player doing nothing")
    elif action == 1:
        agent_host.sendCommand("strafe -1")
        print("Moving foward")
    elif action == 2:
        agent_host.sendCommand("move -1")
        print("Moving left")
    elif action == 3:
        agent_host.sendCommand("move 1")
        print("Moving right")
    elif action == 4:
        agent_host.sendCommand("jumpstrafe -1")
        print("Forward Jump")
    elif action == 5:
        agent_host.sendCommand("jumpmove -1")
        print("Left Jump")
    elif action == 6:
        agent_host.sendCommand("jumpmove 1")
        print("Right Jump")
    else:
        print("Unknown output from Keras network")

# Loop until mission ends:
while world_state.is_mission_running:
    #print(".", end="")
    time.sleep(0.1)
    world_state = agent_host.getWorldState()
    for error in world_state.errors:
        print("Error:",error.text)
    if world_state.number_of_observations_since_last_state > 0: # Have any observations come in?
        msg = world_state.observations[-1].text                 # Yes, so get the text
        observations = json.loads(msg)                          # and parse the JSON
        grid1 = observations.get(u'floor1', 0)                 # and get the grid we asked for
        grid2 = observations.get(u'floor2', 0)                 # and get the grid we asked for
        grid3 = observations.get(u'floor3', 0)                 # and get the grid we asked for
        grid4 = observations.get(u'floor4', 0)                 # and get the grid we asked for
        direction, state = get_state(grid1, grid2, grid3, grid4, observations.get(u'Yaw', 0))
        pprint.pprint(state)
        # Send state to keras network, which then evaluates action.
        prediction = loaded_model.predict(np.asarray([state]))
        action = np.argmax(prediction)
        print(action)
        move(observations.get(u'XPos', 0), observations.get(u'YPos', 0), observations.get(u'ZPos', 0), direction, action)

print()
print("Mission ended")
# Mission has ended.
