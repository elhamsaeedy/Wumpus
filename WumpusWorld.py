# -*- coding: utf-8 -*-
"""
Created on Sat Oct 10 14:33:42 2020

@author: elham
"""

from environment import Coords, Environment, Percept
from agent import Agent
from AgentType import NaiveAgent
import random

def runEpisode(env,agent,percept):
    NextAction=agent.nextAction()
    print(NextAction)
    (NewEnv,NewPercept)=env.applyAction(NextAction)
    NewEnv.visualize()
    #print(NewEnv)
    #print(NewEnv.agent)
    print("Agent orientaion=",NewEnv.agent.orientation)
    print(NewPercept)
    return (NewEnv,NewPercept)

def initialize(gridwidth, gridheigth, pitProb, allowClimbWithoutGold):
    def randomLocationExceptOrigin():
        x=random.randrange(gridwidth)
        y=random.randrange(gridheigth)
        if x==0 and y==0:
            randomLocationExceptOrigin()
        else:
            location=Coords(x,y)
        return location

    CellIndexes=[]
    for x in range(gridwidth):
        for y in range(gridheigth):
             CellIndexes.append(Coords(x,y))
    FilteredCellIndexes=[CellIndex for CellIndex in CellIndexes if CellIndex!=Coords(x=0,y=0)]
    pitLocations=[CellIndex for CellIndex in FilteredCellIndexes if random.random()<0.2]
    agent=Agent(Coords(0,0),"East", False, True, True)

    environment=Environment(gridwidth, gridheigth, pitProb, allowClimbWithoutGold,agent,pitLocations,False,randomLocationExceptOrigin(),True,randomLocationExceptOrigin())
    percept=Percept(environment.isStench(), environment.isBreeze(), environment.isGlitter(), False, False, environment.terminated, 0)
    #environment.agent=NaiveAgent(percept)
    return (environment,percept)

E=initialize(4, 4, 0.2, False)

A=NaiveAgent(E[1])
NewEnv=E[0]
NewPercept=E[1]

TR=0
while not NewEnv.terminated:
    (NewEnv,NewPercept)=runEpisode(NewEnv,A,NewPercept)
    TR+=NewPercept.reward
    print("Total Reward=",TR )