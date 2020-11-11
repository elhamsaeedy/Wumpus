# -*- coding: utf-8 -*-
"""
Created on Fri Oct  9 07:16:48 2020

@author: elham
"""

from collections import namedtuple
from AgentState import AgentState
import numpy as np
from pomegranate import *
from itertools import combinations

class Coords(namedtuple('Coords', 'x y')):

    def __deepcopy__(self, memodict={}):
        # These are very immutable.   
        return self  
    
class Percept(namedtuple('Percept', 'stench breeze glitter bump scream isTerminated reward')):
    def show():
        return ("stench" if stench else "No Stench", "breeze" if breeze else "No breeze", "glitter" if glitter else "No glitter", "bump" if bump else "No bump", "scream" if scream else "No scream", "isTerminated" if isTerminated else "Not terminated", reward)
              

class Environment(namedtuple('Environment', 'gridwidth gridheight pitProb allowClimbWithoutGold agent pitLocations terminated wumpuslocation wumpusAlive goldlocation')):
    def AdjcentCells(self,coords):
        below=Coords(coords.x - 1, coords.y) if coords.x > 0 else "NA"
        above=Coords(coords.x + 1, coords.y) if coords.x+1 < self.gridwidth else "NA"
        toLeft=Coords(coords.x, coords.y - 1) if coords.y > 0 else "NA"
        toRight=Coords(coords.x, coords.y + 1) if coords.y+1 < self.gridheight else "NA"
            
        return [below,above,toLeft,toRight]
    
    def isPitAt(self,coords):
        return coords in self.pitLocations

    def isWumpusAt(self,coords):
        return coords.x == self.wumpuslocation.x and coords.y== self.wumpuslocation.y

    def isAgentAt(self,coords):
        return coords == self.agent.location
    
    def isGoldAt(self,coords):
        return coords == self.goldlocation
    
    def isPitAdjacent(self):
        return any(i in self.pitLocations for i in self.AdjcentCells(self.agent.location))
    
    def iswumpusAdjacent(self): 
        return self.wumpuslocation in self.AdjcentCells(self.agent.location)
    
    def isGlitter(self):
         return self.goldlocation == self.agent.location

    def isBreeze(self):
         return self.isPitAdjacent()

    def isStench(self):
        return (self.iswumpusAdjacent() and self.wumpusAlive) or (self.isWumpusAt(self.agent.location) and self.wumpusAlive)
        
    def killAttemptSuccessful(self):
        def wumpusInLineOfFire():
            if self.agent.orientation=="West":
                return self.agent.location.x > self.wumpuslocation.x and self.agent.location.y==self.wumpuslocation.y
            elif self.agent.orientation=="East": 
                return self.agent.location.x < self.wumpuslocation.x and self.agent.location.y==self.wumpuslocation.y
            elif self.agent.orientation=="South": 
                return self.agent.location.x == self.wumpuslocation.x and self.agent.location.y > self.wumpuslocation.y
            else:
                return self.agent.location.x == self.wumpuslocation.x and self.agent.location.y < self.wumpuslocation.y
            
        return self.agent.hasArrow and self.wumpusAlive and wumpusInLineOfFire()
        
    def applyAction(self,action):
        if action=="Forward":
            NewLocation=self.agent.forward(self.gridwidth,self.gridheight)
            death=(self.isWumpusAt(NewLocation) and self.wumpusAlive) or self.isPitAt(NewLocation)
            if death:
                NewAgent=AgentState(self.agent.forward(self.gridwidth,self.gridheight),self.agent.orientation, self.agent.hasGold, self.agent.hasArrow, False)
                NewEnv=Environment(self.gridwidth,self.gridheight,self.pitProb,self.allowClimbWithoutGold,NewAgent,self.pitLocations,True,self.wumpuslocation,self.wumpusAlive,self.goldlocation)
                percept=Percept(NewEnv.isStench(), NewEnv.isBreeze(), NewEnv.isGlitter(), False, False, death, -1001)
            
            elif self.isGoldAt(NewLocation):
                NewAgent=AgentState(self.agent.forward(self.gridwidth,self.gridheight),self.agent.orientation, True, self.agent.hasArrow, self.agent.isAlive)
                NewEnv=Environment(self.gridwidth,self.gridheight,self.pitProb,self.allowClimbWithoutGold,NewAgent,self.pitLocations,self.terminated,self.wumpuslocation,self.wumpusAlive,self.goldlocation)
                percept=Percept(NewEnv.isStench(), NewEnv.isBreeze(), NewEnv.isGlitter(), False, False, death, -1)
                
            elif self.agent.hasGold:
                NewAgent=AgentState(self.agent.forward(self.gridwidth,self.gridheight),self.agent.orientation, True, self.agent.hasArrow, self.agent.isAlive)
                NewEnv=Environment(self.gridwidth,self.gridheight,self.pitProb,self.allowClimbWithoutGold,NewAgent,self.pitLocations,self.terminated,self.wumpuslocation,self.wumpusAlive,NewAgent.location)
                percept=Percept(NewEnv.isStench(), NewEnv.isBreeze(), NewEnv.isGlitter(), False, False, death, -1)
                
            else:
                NewAgent=AgentState(self.agent.forward(self.gridwidth,self.gridheight),self.agent.orientation, self.agent.hasGold, self.agent.hasArrow, self.agent.isAlive)
                NewEnv=Environment(self.gridwidth,self.gridheight,self.pitProb,self.allowClimbWithoutGold,NewAgent,self.pitLocations,self.terminated,self.wumpuslocation,self.wumpusAlive,self.goldlocation)
                percept=Percept(NewEnv.isStench(), NewEnv.isBreeze(), NewEnv.isGlitter(), False, False, NewEnv.terminated, -1)
             
                
        elif action=="TurnLeft":
            NewAgent=AgentState(self.agent.location,self.agent.Turn("Left"), self.agent.hasGold, self.agent.hasArrow, self.agent.isAlive)
            NewEnv=Environment(self.gridwidth,self.gridheight,self.pitProb,self.allowClimbWithoutGold,NewAgent,self.pitLocations,self.terminated,self.wumpuslocation,self.wumpusAlive,self.goldlocation)
            percept=Percept(NewEnv.isStench(), NewEnv.isBreeze(), NewEnv.isGlitter(), False, False, NewEnv.terminated, -1)
        
        elif action=="TurnRight":
            NewAgent=AgentState(self.agent.location,self.agent.Turn("Right"), self.agent.hasGold, self.agent.hasArrow, self.agent.isAlive)
            NewEnv=Environment(self.gridwidth,self.gridheight,self.pitProb,self.allowClimbWithoutGold,NewAgent,self.pitLocations,self.terminated,self.wumpuslocation,self.wumpusAlive,self.goldlocation)
            percept=Percept(NewEnv.isStench(), NewEnv.isBreeze(), NewEnv.isGlitter(), False, False, NewEnv.terminated, -1)
    
        elif action=="Grab":
            NewAgent=AgentState(self.agent.location,self.agent.orientation, self.isGlitter(), self.agent.hasArrow, self.agent.isAlive)
            NewEnv=Environment(self.gridwidth,self.gridheight,self.pitProb,self.allowClimbWithoutGold,NewAgent,self.pitLocations,self.terminated,self.wumpuslocation,self.wumpusAlive,self.goldlocation)
            percept=Percept(NewEnv.isStench(), NewEnv.isBreeze(), NewEnv.isGlitter(), False, False, NewEnv.terminated, -1)
        
        elif action=="Climb":
            success=self.agent.hasGold and self.isAgentAt(Coords(0,0))
            isTerminated=success or self.allowClimbWithoutGold
            NewEnv=Environment(self.gridwidth,self.gridheight,self.pitProb,self.allowClimbWithoutGold,self.agent,self.pitLocations,isTerminated,self.wumpuslocation,self.wumpusAlive,self.goldlocation)
            percept=Percept(NewEnv.isStench(), NewEnv.isBreeze(), NewEnv.isGlitter(), False, False, NewEnv.terminated, 999 if success else -1)
        
        elif action=="Shoot":
            hadArrow=-11 if self.agent.hasArrow else -1
            NewAgent=AgentState(self.agent.location,self.agent.orientation, self.agent.hasGold, False, self.agent.isAlive)
            NewEnv=Environment(self.gridwidth,self.gridheight,self.pitProb,self.allowClimbWithoutGold,NewAgent,self.pitLocations,self.terminated,self.wumpuslocation,self.wumpusAlive and not self.killAttemptSuccessful(),self.goldlocation)
            percept=Percept(NewEnv.isStench(), NewEnv.isBreeze(), NewEnv.isGlitter(), False, False, NewEnv.terminated, hadArrow)
        
        return (NewEnv,percept)
        
    def updatePitProb(self,PitMatrix,PitProbDist,NewPercept,Location,safeLocations):
        AdjCells=self.AdjcentCells(Location) 
        while 'NA' in AdjCells:
            AdjCells.remove('NA')

        PitAdjCells=[]
        for i in AdjCells:
            PitAdjCells.append(PitProbDist[self.gridheight-i.y-1][i.x])        

            #Build breeze ConditionalProbabilityTable
        conditions=[]
        for j in range(len(PitAdjCells)):
            comb = combinations(list(range(len(PitAdjCells))), j+1)
            for i in list(comb): 
                Tlist=np.zeros(len(PitAdjCells), dtype=bool).tolist()
                Flist=np.zeros(len(PitAdjCells), dtype=bool).tolist()
                t=0
                while t<=j:
                    Tlist[i[t]]=True
                    Flist[i[t]]=True
                    t+=1
                Tlist.append(True)
                Tlist.append(1)
                Flist.append(False)
                Flist.append(0)
                conditions.append(Tlist)  
                conditions.append(Flist)
        F1=np.zeros(len(PitAdjCells), dtype=bool).tolist() 
        F1.append(False)
        F1.append(1)
        F2=np.zeros(len(PitAdjCells), dtype=bool).tolist() 
        F2.append(True)
        F2.append(0)
        conditions.append(F1)  
        conditions.append(F2)
    
        breeze=ConditionalProbabilityTable(conditions,PitAdjCells)
    
            #Add state objects
        PitModel= BayesianNetwork("Pits Model")
        p=[]    
        for i in range(len(PitAdjCells)):  
            p.append(State(PitAdjCells[i],name="PitAdjCell"+str(i)))
            PitModel.add_states(p[i])
    
        p.append(State(breeze,name="breeze"))
        PitModel.add_states(p[-1])
    
            #Add edge objects        
        for i in range(len(PitAdjCells)):
            PitModel.add_edge(p[i], p[-1])
    
        PitModel.bake()
    
           #Predict being Pit in any of the adjacent cells
            #Only one or multiple pits are possible
        #Update the probability of current cell and previous adjacent
        if self.agent.isAlive and Location not in safeLocations:
            if PitProbDist[self.gridwidth-Location.y-1][Location.x] != 0.2:
                #Find previous adjacent cells and update prob
                PrevAdj=self.AdjcentCells(safeLocation[-1])
                while 'NA' in PrevAdj:
                    PrevAdj.remove('NA')
                for i in range(len(PrevAdj)):
                    if i==Location:
                        PitProbDist[self.gridwidth-Location.y-1][Location.x]=DiscreteDistribution({True:0,False:1})
                        PitMatrix[self.gridwidth-Location.y-1,Location.x]=0
                    else:
                        PrevScen=[]
                        for i in range(len(PrevAdj)):
                            if i==Location:
                                PrevScen.append(False)
                            else:
                                PrevScen.append(None)
                        PrevScen.append(True)
                        for i in range(len(PrevAdj)):
                            if i!=Location:
                                PitProbDist[self.gridwidth-PrevAdj[i].y-1][PrevAdj[i].x]=PitModel.predict_proba([PrevScen])[0][i]
                                #Update PitMatrix with new PitProb
                                PitMatrix[self.gridwidth-PrevAdj[i].y-1,PrevAdj[i].x]=PitModel.predict_proba([PrevScen])[0][i].parameters[0][True]
    
    
        scen=[None for i in range(len(AdjCells))]
        scen.append(True)
        for i in range(len(AdjCells)):
            PitProbDist[self.gridwidth-AdjCells[i].y-1][AdjCells[i].x]=PitModel.predict_proba([scen])[0][i]
            #Update PitMatrix with new PitProb
            PitMatrix[self.gridwidth-AdjCells[i].y-1,AdjCells[i].x]=PitModel.predict_proba([scen])[0][i].parameters[0][True]
    
    
        return (PitMatrix,PitProbDist)
      
    def updateWumpusProb(self,WumpusProb,WumpusMatrix,WumpusProbDist,NewPercept,Location,safeLocations):
        AdjCells=self.AdjcentCells(Location) 
        while 'NA' in AdjCells:
            AdjCells.remove('NA')
    
        WumpAdjCells=[]
        for i in AdjCells:
            WumpAdjCells.append(WumpusProbDist[self.gridheight-i.y-1][i.x])        
    
            #Build breeze ConditionalProbabilityTable
        conditions=[]
        for j in range(len(WumpAdjCells)):
            comb = combinations(list(range(len(WumpAdjCells))), j+1)
            for i in list(comb): 
                Tlist=np.zeros(len(WumpAdjCells), dtype=bool).tolist()
                Flist=np.zeros(len(WumpAdjCells), dtype=bool).tolist()
                t=0
                while t<=j:
                    Tlist[i[t]]=True
                    Flist[i[t]]=True
                    t+=1
                Tlist.append(True)
                Tlist.append(1)
                Flist.append(False)
                Flist.append(0)
                conditions.append(Tlist)  
                conditions.append(Flist)
        F1=np.zeros(len(WumpAdjCells), dtype=bool).tolist() 
        F1.append(False)
        F1.append(1)
        F2=np.zeros(len(WumpAdjCells), dtype=bool).tolist() 
        F2.append(True)
        F2.append(0)
        conditions.append(F1)  
        conditions.append(F2)
    
        stench=ConditionalProbabilityTable(conditions,WumpAdjCells)
    
            #Add state objects
        WumpusModel= BayesianNetwork("Pits Model")
        p=[]    
        for i in range(len(WumpAdjCells)):  
            p.append(State(WumpAdjCells[i],name="WumpusAdjCell"+str(i)))
            WumpusModel.add_states(p[i])
    
        p.append(State(stench,name="stench"))
        WumpusModel.add_states(p[-1])
    
            #Add edge objects        
        for i in range(len(WumpAdjCells)):
            WumpusModel.add_edge(p[i], p[-1])
    
        WumpusModel.bake()
    
            #Predict being Wumpus in any of the adjacent cells
            #Only one wumpus is possible
        scen=[]
        for i in AdjCells:
            if i not in safeLocations:
                scen.append(None)
            else:
                scen.append(False)
        scen.append(True)
        
        #update WumpusProbDist and Wumpus Matrix
        for x in range(self.gridwidth):
            for y in range(self.gridheight):
                if Coords(x,y) not in AdjCells:
                    WumpusProbDist[self.gridwidth-y-1][x]=DiscreteDistribution({True:0,False:1})
                    WumpusMatrix[self.gridwidth-y-1,x]=0
                else:
                    index = AdjCells.index(Coords(x,y))
                    if scen[index]==None:
                        WumpusProbDist[self.gridwidth-y-1][x]=WumpusModel.predict_proba([scen])[0][index]
                        WumpusMatrix[self.gridwidth-y-1,x]=WumpusModel.predict_proba([scen])[0][index].parameters[0][True]
                    else:
                        WumpusProbDist[self.gridwidth-y-1][x]=DiscreteDistribution({True:0,False:1})
                        WumpusMatrix[self.gridwidth-y-1,x]=0
                        
        return (WumpusMatrix,WumpusProbDist)
        
    def visualize(self):
        wumpusSymbol="W" if self.wumpusAlive else "w"
        for y in range(self.gridheight-1, -1, -1): 
            c=[]
            x=0
            for x in range(0,self.gridwidth):
                if self.isAgentAt(Coords(x,y)):
                    c.append("A")
                    c[x]+="P" if self.isPitAt(Coords(x,y)) else " "
                    c[x]+="G" if self.isGoldAt(Coords(x,y)) else " "
                    c[x]+=wumpusSymbol if self.isWumpusAt(Coords(x,y)) else " "
                    c[x]+="|"
                    
                elif self.isPitAt(Coords(x,y)):
                    c.append("P")
                    c[x]+="G" if self.isGoldAt(Coords(x,y)) else " "
                    c[x]+=wumpusSymbol if self.isWumpusAt(Coords(x,y)) else " "
                    c[x]+=" |"
                    
                elif self.isGoldAt(Coords(x,y)):
                    c.append("G")
                    c[x]+=wumpusSymbol if self.isWumpusAt(Coords(x,y)) else " "
                    c[x]+="  |"
                    
                elif self.isWumpusAt(Coords(x,y)):
                    c.append(wumpusSymbol)
                    c[x]+="   |"
                else:
                    c.append("    |")
            print(c) 
            
# Initialize a game
import random
def apply(gridwidth, gridheigth, pitProb, allowClimbWithoutGold):
    def randomLocationExceptOrigin():
        x=random.randrange(gridwidth)
        y=random.randrange(gridheigth)
        if x==0 and y==0:
            randomLocationExceptOrigin() 
        else:
            Coords(x,y)
        return Coords
    
    CellIndexes=[]
    for x in range(gridwidth):
        for y in range(gridheigth):
            CellIndexes.append(Coords(x,y))   
    FilteredCellIndexes=[CellIndex for CellIndex in CellIndexes if CellIndex!=Coords(x=0,y=0)]
    pitLocations=[CellIndex for CellIndex in FilteredCellIndexes if random.random()<0.2]
    
    environment=Environment(gridwidth, gridheigth, pitProb, allowClimbWithoutGold,AgentState(),pitLocations,False,randomLocationExceptOrigin(),True,randomLocationExceptOrigin())
    percept=Percept(environment.isStench(), environment.isBreeze(), environment.isGlitter(), False, False, environment.terminated, 0)
    return (environment,percept)
    