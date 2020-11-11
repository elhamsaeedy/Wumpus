# -*- coding: utf-8 -*-
"""
Created on Fri Oct  9 08:06:19 2020

@author: elham
"""

from environment import Coords, Environment, Percept
from agent import Agent
from Astar import Node, astar
from Movement import movement
from collections import namedtuple
import random
import numpy as np

class ProbAgent(namedtuple('ProbAgent', 'gridwidth gridheight agentState safeLocations stenchLocations breezeLocations')):  
    def constructBeelinePlan(self):
        maze=np.ones((self.gridwidth,self.gridheight))
        for i in range(self.gridwidth):
            for j in range(self.gridheight):
                loc=Coords(i,j)
                if loc in self.safeLocations:
                    maze[self.gridheight-loc.y-1][loc.x]=0
        start=(self.gridheight-self.agentState.location.y-1,self.agentState.location.x)
        end=(self.gridheight-1,0)
        print(maze)
        path = astar(maze, start, end)
        BPlan=[]
        for cells in path.plan():
            BPlan.append(Coords(cells[1],self.gridheight-1-cells[0]))
        print ("Beeline Plan: ", BPlan)
        return BPlan
        
    def NextRandomAction(self):
        randGen=random.randrange(4)
        if randGen==0:
            return "Forward"
        elif randGen==1:
            return "TurnLeft"
        elif randGen==2:
            return "TurnRight"
        elif randGen==3:
            return "Shoot"
        
    def NextSafestAction(self,NewEnv,PitMatrix,WumpusMatrix):
        AdjCells=NewEnv.AdjcentCells(self.agentState.location)
        PitAdj=[]
        WumpAdj=[]
        for i in AdjCells:
            if i=="NA" or i in self.safeLocations:
                PitAdj.append(100)
                WumpAdj.append(100)
            else:
                PitAdj.append(PitMatrix[self.gridwidth-i.y-1,i.x])
                WumpAdj.append(WumpusMatrix[self.gridwidth-i.y-1,i.x])  
        
        OriginalHazard=[a + b for a, b in zip(PitAdj, WumpAdj)]
        SortedHazard=[a + b for a, b in zip(PitAdj, WumpAdj)]
        SortedHazard.sort()
        dest=[]
        for i in SortedHazard:
            if AdjCells[OriginalHazard.index(i)] not in self.safeLocations and PitAdj[OriginalHazard.index(i)]!=1 and WumpAdj[OriginalHazard.index(i)]!=1:
                dest.append(AdjCells[OriginalHazard.index(i)])  
                
        if len(dest)>0:
            destination=dest[0]
        else:
            destination=self.safeLocations[-2]
        action=[]
        (NextAction,NewOrientation)=movement(action,destination,self.agentState.location,self.agentState.orientation).AdjustOrientation()
        return NextAction
        
    
class BeelineAgent(namedtuple('BeelineAgent', 'gridwidth gridheight agentState safeLocations')):  
    def constructBeelinePlan(self):
        maze=np.ones((self.gridwidth,self.gridheight))
        for i in range(self.gridwidth):
            for j in range(self.gridheight):
                loc=Coords(i,j)
                if loc in self.safeLocations:
                    maze[self.gridheight-loc.y-1][loc.x]=0
        start=(self.gridheight-self.agentState.location.y-1,self.agentState.location.x)
        end=(self.gridheight-1,0)
        print(maze)
        path = astar(maze, start, end)
        BPlan=[]
        for cells in path.plan():
            BPlan.append(Coords(cells[1],self.gridheight-1-cells[0]))
        print ("Beeline Plan: ", BPlan)
        return BPlan
        
    def nextAction(self):

        randGen=random.randrange(4)
        if randGen==0:
            return "Forward"
        elif randGen==1:
            return "TurnLeft"
        elif randGen==2:
            return "TurnRight"
        elif randGen==3:
            return "Shoot"


class NaiveAgent(namedtuple('NaiveAgent', 'percept')):
    
    def nextAction(self):

        randGen=random.randrange(6)
        if randGen==0:
            return "Forward"
        elif randGen==1:
            return "TurnLeft"
        elif randGen==2:
            return "TurnRight"
        elif randGen==3:
            return "Grab"
        elif randGen==4:
            return "Climb"        
        elif randGen==5:
            return "Shoot"