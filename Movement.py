# -*- coding: utf-8 -*-
"""
Created on Fri Oct 23 10:17:59 2020

@author: elham
"""
from collections import namedtuple

class movement(namedtuple('movement', 'Action nextCell currentCell cuurentOrientation')):
    
    def AdjustOrientation(self):  
        NextAction=self.Action
        if self.currentCell.x==self.nextCell.x and self.currentCell.y>self.nextCell.y:
            if self.cuurentOrientation=="East":
                NextAction.append("TurnRight")
                NextAction.append("Forward")
                NewOrientation="South"
            elif self.cuurentOrientation=="West":
                NextAction.append("TurnLeft")
                NextAction.append("Forward")
                NewOrientation="South"
            elif self.cuurentOrientation=="North":
                NextAction.append("TurnLeft")
                NextAction.append("TurnLeft")
                NextAction.append("Forward")
                NewOrientation="South"
            else:
                NewOrientation="South"
                NextAction.append("Forward")
                return (NextAction,NewOrientation)
            
        elif self.currentCell.x==self.nextCell.x and self.currentCell.y<self.nextCell.y:
            
            if self.cuurentOrientation=="East":
                NextAction.append("TurnLeft")
                NextAction.append("Forward")
                NewOrientation="North"
            elif self.cuurentOrientation=="West":
                NextAction.append("TurnRight")
                NextAction.append("Forward")
                NewOrientation="North"
            elif self.cuurentOrientation=="South":
                NextAction.append("TurnLeft")
                NextAction.append("TurnLeft")
                NextAction.append("Forward")
                NewOrientation="North"
            else:
                NewOrientation="North"
                NextAction.append("Forward")
                return (NextAction,NewOrientation)
                
        elif self.currentCell.y==self.nextCell.y and self.currentCell.x<self.nextCell.x:
            
            if self.cuurentOrientation=="South":
                NextAction.append("TurnLeft")
                NextAction.append("Forward")        
                NewOrientation="East"
            elif self.cuurentOrientation=="North":
                NextAction.append("TurnRight")
                NextAction.append("Forward") 
                NewOrientation="East"
            elif self.cuurentOrientation=="West":
                NextAction.append("TurnLeft")
                NextAction.append("TurnLeft")
                NextAction.append("Forward") 
                NewOrientation="East"
            else:
                NewOrientation="East"
                NextAction.append("Forward") 
                return (NextAction,NewOrientation)
            
        elif self.currentCell.y==self.nextCell.y and self.currentCell.x>self.nextCell.x:
            if self.cuurentOrientation=="South":
                NextAction.append("TurnRight")
                NextAction.append("Forward") 
                NewOrientation="West"
            elif self.cuurentOrientation=="North":
                NextAction.append("TurnLeft")
                NextAction.append("Forward") 
                NewOrientation="West"
            elif self.cuurentOrientation=="East":
                NextAction.append("TurnLeft")
                NextAction.append("TurnLeft")
                NextAction.append("Forward") 
                NewOrientation="West"
            else:
                NewOrientation="West"
                NextAction.append("Forward") 
                return (NextAction,NewOrientation)
        else:
            NewOrientation=self.cuurentOrientation
            NextAction.append("Forward") 
            
        return (NextAction,NewOrientation)