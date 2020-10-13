# -*- coding: utf-8 -*-
"""
Created on Fri Oct  9 07:16:48 2020

@author: elham
"""

from collections import namedtuple
from agent import Agent

class Coords(namedtuple('Coords', 'x y')):

    def __deepcopy__(self, memodict={}):
        # These are very immutable.   
        return self  
    
class Percept(namedtuple('Percept', 'stench breeze glitter bump scream isTerminated reward')):
    def show():
        return ("stench" if stench else "No Stench", "breeze" if breeze else "No breeze", "glitter" if glitter else "No glitter", "bump" if bump else "No bump", "scream" if stench else "No scream", "isTerminated" if isTerminated else "Not terminated", reward)
              

class Environment(namedtuple('Environment', 'gridwidth gridheight pitProb allowClimbWithoutGold agent pitLocations terminated wumpuslocation wumpusAlive goldlocation')):
    def AdjcentCells(self,coords):
        below=Coords(coords.x - 1, coords.y) if coords.x > 0 else "NA"
        above=Coords(coords.x + 1, coords.y) if coords.x < self.gridwidth else "NA"
        toLeft=Coords(coords.x, coords.y - 1) if coords.y > 0 else "NA"
        toRight=Coords(coords.x, coords.y + 1) if coords.y < self.gridheight else "NA"
            
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
        return self.iswumpusAdjacent() or self.isWumpusAt(self.agent.location)
        
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
                NewAgent=Agent(self.agent.forward(self.gridwidth,self.gridheight),self.agent.orientation, self.agent.hasGold, self.agent.hasArrow, False)
                NewEnv=Environment(self.gridwidth,self.gridheight,self.pitProb,self.allowClimbWithoutGold,NewAgent,self.pitLocations,True,self.wumpuslocation,self.wumpusAlive,self.goldlocation)
                percept=Percept(NewEnv.isStench(), NewEnv.isBreeze(), NewEnv.isGlitter(), False, False, death, -1001)
                    
            else:
                NewAgent=Agent(self.agent.forward(self.gridwidth,self.gridheight),self.agent.orientation, self.agent.hasGold, self.agent.hasArrow, self.agent.isAlive)
                NewEnv=Environment(self.gridwidth,self.gridheight,self.pitProb,self.allowClimbWithoutGold,NewAgent,self.pitLocations,self.terminated,self.wumpuslocation,self.wumpusAlive,self.goldlocation)
                percept=Percept(NewEnv.isStench(), NewEnv.isBreeze(), NewEnv.isGlitter(), False, False, NewEnv.terminated, -1)
             
                
        elif action=="TurnLeft":
            NewAgent=Agent(self.agent.location,self.agent.Turn("Left"), self.agent.hasGold, self.agent.hasArrow, self.agent.isAlive)
            NewEnv=Environment(self.gridwidth,self.gridheight,self.pitProb,self.allowClimbWithoutGold,NewAgent,self.pitLocations,self.terminated,self.wumpuslocation,self.wumpusAlive,self.goldlocation)
            percept=Percept(NewEnv.isStench(), NewEnv.isBreeze(), NewEnv.isGlitter(), False, False, NewEnv.terminated, -1)
        
        elif action=="TurnRight":
            NewAgent=Agent(self.agent.location,self.agent.Turn("Right"), self.agent.hasGold, self.agent.hasArrow, self.agent.isAlive)
            NewEnv=Environment(self.gridwidth,self.gridheight,self.pitProb,self.allowClimbWithoutGold,NewAgent,self.pitLocations,self.terminated,self.wumpuslocation,self.wumpusAlive,self.goldlocation)
            percept=Percept(NewEnv.isStench(), NewEnv.isBreeze(), NewEnv.isGlitter(), False, False, NewEnv.terminated, -1)
    
        elif action=="Grab":
            NewAgent=Agent(self.agent.location,self.agent.orientation, self.isGlitter(), self.agent.hasArrow, self.agent.isAlive)
            NewEnv=Environment(self.gridwidth,self.gridheight,self.pitProb,self.allowClimbWithoutGold,NewAgent,self.pitLocations,self.terminated,self.wumpuslocation,self.wumpusAlive,self.goldlocation)
            percept=Percept(NewEnv.isStench(), NewEnv.isBreeze(), NewEnv.isGlitter(), False, False, NewEnv.terminated, -1)
        
        elif action=="Climb":
            success=self.agent.hasGold and self.agent.location==Coords(0,0)
            isTerminated=success or self.allowClimbWithoutGold
            NewEnv=Environment(self.gridwidth,self.gridheight,self.pitProb,self.allowClimbWithoutGold,self.agent,self.pitLocations,isTerminated,self.wumpuslocation,self.wumpusAlive,self.goldlocation)
            percept=Percept(NewEnv.isStench(), NewEnv.isBreeze(), NewEnv.isGlitter(), False, False, NewEnv.terminated, 999 if success else -1)
        
        elif action=="Shoot":
            hadArrow=-11 if self.agent.hasArrow else -1
            NewAgent=Agent(self.agent.location,self.agent.orientation, self.agent.hasGold, False, self.agent.isAlive)
            NewEnv=Environment(self.gridwidth,self.gridheight,self.pitProb,self.allowClimbWithoutGold,NewAgent,self.pitLocations,self.terminated,self.wumpuslocation,self.wumpusAlive and not self.killAttemptSuccessful(),self.goldlocation)
            percept=Percept(NewEnv.isStench(), NewEnv.isBreeze(), NewEnv.isGlitter(), False, False, NewEnv.terminated, hadArrow)
        
        return (NewEnv,percept)
        
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
    
    environment=Environment(gridwidth, gridheigth, pitProb, allowClimbWithoutGold,Agent(),pitLocations,False,randomLocationExceptOrigin(),True,randomLocationExceptOrigin())
    percept=Percept(environment.isStench(), environment.isBreeze(), environment.isGlitter(), False, False, environment.terminated, 0)
    return (environment,percept)
    