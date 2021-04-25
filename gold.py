import math, pygame
from pygame import Rect

#This class represent the "gold nugget" that the player must collect
class Gold:
    # Constructor (self, x position, y position)
    def __init__(self, x, y):
        
        #use the passed parameters to (re)set the bullet
        self.setup( x, y )
        
        #Activate automatically when constructed
        self.active=True
        
    # Activate / Desactivate / check activity state    
    def isActive(self):
        return self.active
    def setOn(self):
        self.active=True
    def setOff(self):
        self.active=False
    
    #Set the bullet initial params
    # Param ( surface to draw into, collision mask to check with)
    def setup( self, x, y ):
        
        #use the passed parameters to (re)set the bullet
        self.x=x
        self.y=y
    
    # Move the bullet with its internal variable, and perform collision with the defined background surface / hitmask
    # Param ( X speed, Y speed)
    def move( self, speedX, speedY ):
        
        #if we are still active
        if self.isActive() == True:
        
            #Update the bullet with the speed vars
            self.x += speedX
            self.y += speedY
            
            #If we are out of bounds, kill us 
            if self.isActive() == True and (self.y < -32 ):
                #Desactivate us
                self.setOff()
    

    # Check if we are "collected" by the rect (ideally the player rect) and return true if it's the case
    # Param ( Rect to check collision with )
    def isCollected( self, playerRect ):
        
        #if we collide with the player (simple AABB collision)
        if playerRect.colliderect( (int(self.x)-3, int(self.y)-3, 6, 6)  ):
        
            #Desactivate us
            self.setOff()
        
            #Notify the game of the collision (as the game handles score and all stuffs like that
            return True
        
        #Else, no collision for now!
        else:
            return False
    
    
    
    # Draw the bullet on the specified surface
    # Param ( surface to draw into)
    def render( self, display ):    
        pygame.draw.circle(display, (255,255,0,255), (int(self.x-3), int(self.y-3)), 6 )
        