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

if sys.version_info[0] == 2:
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)  # flush print output immediately
else:
    import functools
    print = functools.partial(print, flush=True)


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
            if up_or_down == 1:
                # Fill in ugly holes
                genstring += '<DrawBlock x="%d" y="%d" z="%d" type="dirt"/>\n' % (i+starting_x, up_or_down+y_offset+starting_y-1, n+starting_z)
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
                  <ContinuousMovementCommands turnSpeedDegs="180"/>
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

"""agent_host.sendCommand("hotbar.9 1")
agent_host.sendCommand("hotbar.9 0")

agent_host.sendCommand("pitch 0.2")
time.sleep(1)
agent_host.sendCommand("pitch 0")
agent_host.sendCommand("move 1")
time.sleep(5)
agent_host.sendCommand("move 0")
time.sleep(2)
agent_host.sendCommand("use 1")
time.sleep(5)
agent_host.sendCommand("attack 0")
print("Done with commands")"""
agent_host.sendCommand("turn -1")
time.sleep(1)
agent_host.sendCommand("turn 0")
agent_host.sendCommand("move 1")
agent_host.sendCommand("move 0")
agent_host.sendCommand("move 1")
time.sleep(5)

# Loop until mission ends:
while world_state.is_mission_running:
    print(".", end="")
    time.sleep(0.1)
    world_state = agent_host.getWorldState()
    for error in world_state.errors:
        print("Error:",error.text)

print()
print("Mission ended")
# Mission has ended.
