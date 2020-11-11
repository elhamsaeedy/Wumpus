# -*- coding: utf-8 -*-
"""
Created on Mon Nov  9 20:03:29 2020

@author: elham
"""

from environment import Coords, Environment, Percept
from agent import Agent
from Movement import movement
from AgentType import ProbAgent
import random
import numpy as np
from pomegranate import *
from itertools import combinations

def runEpisode(NewEnv,P,percept,TR,safeLocations,stenchLocations,breezeLocations,PitMatrix,PitProbDist,WumpusMatrix,WumpusProbDist,WumpusProb):
    
    TotalReward=TR
    if NewEnv.isGoldAt(P.agentState.location): 
        safeLocations.append(NewEnv.agent.location)
        print("Safe Loctaion=", safeLocations)
        BeelineAction=["Grab"]
        BPlan=P.constructBeelinePlan()
        BPlan.pop(0)
        i=0
        
        while not NewEnv.isAgentAt(Coords(0,0)):
            (BeelineAction,NewOrientation)=movement(BeelineAction,BPlan[i], NewEnv.agent.location, NewEnv.agent.orientation).AdjustOrientation()
            for j in BeelineAction:
                print("Action: ",j)
                (NewEnv,per)=NewEnv.applyAction(j)
                TotalReward+=per.reward
                NewEnv.visualize()
                print(NewEnv.agent.orientation)
                print("Total Reward=",TotalReward )
                
            if not NewEnv.isAgentAt(Coords(0,0)):    
                BeelineAction=[]     
            else:
                (NewEnv,per)=NewEnv.applyAction("Climb")
            
            i+=1
            
        (NewEnv,per)=NewEnv.applyAction("Climb")
        TotalReward+=per.reward
        NewEnv.visualize()
        print("Agent ",NewEnv.agent)
        print("Action: Climb")
        print("Total Reward=",TotalReward )
        return (NewEnv,per,TotalReward,safeLocations,stenchLocations,breezeLocations,PitMatrix,PitProbDist,WumpusMatrix,WumpusProbDist,WumpusProb)
    else:
        PrevLoc=NewEnv.agent.location
        NextAction=P.NextSafestAction(NewEnv,PitMatrix,WumpusMatrix)
        print(NextAction[0])
        (NewEnv,per)=NewEnv.applyAction(NextAction[0])
        TotalReward+=per.reward
        
        if NewEnv.agent.isAlive and NewEnv.agent.location not in safeLocations:
            safeLocations.append(NewEnv.agent.location)
            PrevPitProb=PitMatrix[gridwidth-NewEnv.agent.location.y-1,NewEnv.agent.location.x]
            PitProbDist[NewEnv.gridwidth-NewEnv.agent.location.y-1][NewEnv.agent.location.x]=DiscreteDistribution({True:0,False:1})
            PitMatrix[NewEnv.gridwidth-NewEnv.agent.location.y-1,NewEnv.agent.location.x]=0
            if PrevPitProb > 0.2: 
                (PitMatrix,PitProbDist)=NewEnv.updatePitProb(PitMatrix,PitProbDist,NewPercept,PrevLoc,safeLocations)
                
            PrevWumpusProb=WumpusMatrix[NewEnv.gridwidth-NewEnv.agent.location.y-1,NewEnv.agent.location.x]            
            if NewEnv.wumpusAlive:
                WumpusMatrix[NewEnv.gridwidth-NewEnv.agent.location.y-1,NewEnv.agent.location.x]=0
                WumpusProbDist[NewEnv.gridwidth-NewEnv.agent.location.y-1][NewEnv.agent.location.x]=DiscreteDistribution({True:0,False:1})
                if PrevWumpusProb < 0.25 and np.all(WumpusMatrix < 0.25):
                    WumpusMatrix/=WumpusProb
                    WumpusProb=1/(NewEnv.gridwidth*NewEnv.gridheight-len(safeLocations)) 
                    WumpusMatrix*=WumpusProb
                    WumpusProbDist[NewEnv.gridwidth-NewEnv.agent.location.y-1][NewEnv.agent.location.x]=DiscreteDistribution({True:0,False:1})                  
                elif 1 not in WumpusMatrix:
                    (WumpusMatrix,WumpusProbDist)=NewEnv.updateWumpusProb(WumpusProb,WumpusMatrix,WumpusProbDist,NewPercept,PrevLoc,safeLocations)

        if not NewEnv.wumpusAlive:
                    WumpusMatrix=np.zeros((gridwidth,gridheight))
                    #Wumpus distribution for each cell
                    WumpusProbDist=[["" for i in range(gridwidth)] for i in range(gridheight)]
                    for i in range(gridwidth):
                        for j in range(gridheight):
                            WumpusProbDist[i][j]=DiscreteDistribution({True:0,False:1})
        
                               
        if per.stench and NewEnv.agent.location not in stenchLocations and 1 not in WumpusMatrix:
            stenchLocations.append(NewEnv.agent.location)
            (WumpusMatrix,WumpusProbDist)=NewEnv.updateWumpusProb(WumpusProb,WumpusMatrix,WumpusProbDist,NewPercept,NewEnv.agent.location,safeLocations)
        if per.breeze and NewEnv.agent.location not in breezeLocations:
            breezeLocations.append(NewEnv.agent.location)
            (PitMatrix,PitProbDist)=NewEnv.updatePitProb(PitMatrix,PitProbDist,NewPercept,NewEnv.agent.location,safeLocations)
        
        NewEnv.visualize()
        print("Pit prob matrix: ")
        print(PitMatrix)
        print("Wumpus prob matrix: ")
        print(WumpusMatrix)
        print("Agent ",NewEnv.agent)
        print(per)
        print("Safe Loctaion=", safeLocations)
        print("Stench Loctaion=", stenchLocations)
        print("Breeze Loctaion=", breezeLocations)
        print("Total Reward=",TotalReward )

        return (NewEnv,per,TotalReward,safeLocations,stenchLocations,breezeLocations,PitMatrix,PitProbDist,WumpusMatrix,WumpusProbDist,WumpusProb)
    
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
    
        #Pit probability matrix
    PitMatrix=np.ones((gridwidth,gridheight))
    PitMatrix*=pitProb
    PitMatrix[gridheight-1][0]=0
    
    #Pit distribution for each cell
    PitProbDist=[["" for i in range(gridwidth)] for i in range(gridheight)]
    for i in range(gridwidth):
        for j in range(gridheight):
            if i == gridheight-1 and j == 0:
                PitProbDist[i][j]=DiscreteDistribution({True:0,False:1})
            else:
                PitProbDist[i][j]=DiscreteDistribution({True:pitProb,False:(1-pitProb)})
        
    #Wumpus probability matrix
    WumpusMatrix=np.ones((gridwidth,gridheight))
    WumpusProb=1/(gridwidth*gridheight-1)
    WumpusMatrix*=WumpusProb
    WumpusMatrix[gridheight-1][0]=0
    
    #Wumpus distribution for each cell
    WumpusProbDist=[["" for i in range(gridwidth)] for i in range(gridheight)]
    for i in range(gridwidth):
        for j in range(gridheight):
            if i == gridheight-1 and j == 0:
                WumpusProbDist[i][j]=DiscreteDistribution({True:0,False:1})
            else:
                WumpusProbDist[i][j]=DiscreteDistribution({True:WumpusProb,False:(1-WumpusProb)})
    
    TR=0
    safeLocations=[Coords(0,0)]
    stenchLocations=[Coords(0,0)] if percept.stench else []
    breezeLocations=[Coords(0,0)] if percept.breeze else []
    heardScream=False
    
    if percept.stench:
        (WumpusMatrix,WumpusProbDist)=environment.updateWumpusProb(WumpusProb,WumpusMatrix,WumpusProbDist,percept,environment.agent.location,safeLocations)
    if percept.breeze:
        (PitMatrix,PitProbDist)=environment.updatePitProb(PitMatrix,PitProbDist,percept,environment.agent.location,safeLocations)

    return (environment,percept,TR,safeLocations,stenchLocations,breezeLocations,PitMatrix,PitProbDist,WumpusMatrix,WumpusProbDist,WumpusProb)

gridwidth=4
gridheight=4
pitProbability=0.2
E=initialize(gridwidth, gridheight, pitProbability, False)
NewEnv=E[0]
NewPercept=E[1]
E[0].visualize()
PitMatrix=E[6]
PitProbDist=E[7]
WumpusMatrix=E[8]
WumpusProbDist=E[9]
safeLocations=E[3]
stenchLocations=E[4]
breezeLocations=E[5]
WumpusProb=E[10]
TR=E[2]
print("Pit prob matrix: ")
print(PitMatrix)
print("Wumpus prob matrix: ")
print(WumpusMatrix)
print("Safe Loctaion=", safeLocations)
print("Stench Loctaion=", stenchLocations)
print("Breeze Loctaion=", breezeLocations)
print("Total Reward=",TR )

while not NewEnv.terminated:
    P=ProbAgent(NewEnv.gridwidth,NewEnv.gridheight,NewEnv.agent,safeLocations,stenchLocations,breezeLocations)
    (NewEnv,NewPercept,TR,safeLocations,stenchLocations,breezeLocations,PitMatrix,PitProbDist,WumpusMatrix,WumpusProbDist,WumpusProb)=runEpisode(NewEnv,P,NewPercept,TR,safeLocations,stenchLocations,breezeLocations,PitMatrix,PitProbDist,WumpusMatrix,WumpusProbDist,WumpusProb)

PitLocations=[]
WumpusLocation=[]
for i in range(NewEnv.gridwidth):
    for j in range(NewEnv.gridheight):
        if PitMatrix[i,j]==1:
            PitLocations.append(Coords(j,NewEnv.gridwidth-i-1))
        if WumpusMatrix[i,j]==1:
            WumpusLocation.append(Coords(j,NewEnv.gridwidth-i-1))
if len(PitLocations)>0:
    print("Pit Locations= ",PitLocations)
if len(WumpusLocation)>0:
    print("Wumpus Location= ",WumpusLocation)
