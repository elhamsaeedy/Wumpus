# -*- coding: utf-8 -*-
"""
Created on Fri Oct  9 07:20:36 2020

@author: elham
"""
from collections import namedtuple

class Coords(namedtuple('Coords', 'x y')):

    def __deepcopy__(self, memodict={}):
        # These are very immutable.   
        return self  
    
class Agent(namedtuple('Agent', 'location orientation hasGold hasArrow isAlive')):
    def forward(self, gridwidth, gridheight):
        if self.orientation=="West":
            agentCoords=Coords(max(0,self.location.x-1),self.location.y)
        elif self.orientation=="East":
            agentCoords=Coords(min(gridwidth-1,self.location.x+1),self.location.y)
        elif self.orientation=="South":
            agentCoords=Coords(self.location.x,max(0,self.location.y-1))
        else:
            agentCoords=Coords(self.location.x,min(gridheight-1,self.location.y+1))
        return agentCoords

    def Turn(self,ro):
        if ro=="Left":
            if self.orientation == "North":
                NewOrientation="West"
            elif self.orientation == "East":
                NewOrientation="North"
            elif self.orientation == "West":
                NewOrientation="South"
            else:
                NewOrientation="East"
        if ro=="Right":
            if self.orientation == "North":
                NewOrientation="East"
            elif self.orientation == "East":
                NewOrientation="South"
            elif self.orientation == "West":
                NewOrientation="North"
            else:
                NewOrientation="West"                
        return NewOrientation
    def __deepcopy__(self, memodict={}):
        # These are very immutable.
        return self