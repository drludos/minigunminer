import math, pygame

#This class represent the "bullet" that the player can fire
class Bullet:
    # Constructor (self, x position, y position, speed, angle)
    def __init__(self, x, y, speed, angle):
        
        #use the passed parameters to (re)set the bullet
        self.setup( x, y, speed, angle )
        
        #Activate automatically when constructed
        self.active=True
        
        #Create a bitmask for us to do collision with the BG
        self.mask=pygame.mask.Mask( (4,4) )
        self.mask.fill()
        
        #Create a bitmask hole for us to do create hole in the background when we hit it!
        self.maskhole=pygame.mask.Mask( (12,12) )
        #Fill the mask but remove 1 pixel at each corner to make it "rounder"
        self.maskhole.fill()
        #self.maskhole.set_at((0,0), 0)
        #self.maskhole.set_at((5,0), 0)
        #self.maskhole.set_at((5,5), 0)
        #self.maskhole.set_at((0,5), 0)
    
    # Activate / Desactivate / check activity state    
    def isActive(self):
        return self.active
    def setOn(self):
        self.active=True
    def setOff(self):
        self.active=False
    
    #Set the bullet initial params
    # Param ( surface to draw into, collision mask to check with)
    def setup( self, x, y, speed, angle ):
        
        #use the passed parameters to (re)set the bullet
        self.x=x
        self.y=y
        self.speed=speed
        self.angle=angle
    
    # Move the bullet with its internal variable, and perform collision with the defined background surface / hitmask
    # Param ( surface to draw into, collision mask to check with, color to use to draw holes)
    def move( self, background, hitmask, color):
        
        #if we are still active
        if self.isActive() == True:
        
            #Update the bullet with our internal vars
            self.x += self.speed*math.cos(math.radians(self.angle))
            self.y += self.speed*math.sin(math.radians(self.angle))
            
            # If we hit the backgroud
            if hitmask.overlap(self.mask, (int(self.x-2), int(self.y-2)) ):
                
                #Dig a hole in the background!
                #pygame.draw.rect( background, color, (self.x-4, self.y-4, 8, 8))
                pygame.draw.circle( background, color, (int(self.x), int(self.y)), 8)
                
                #Update the bitmask of the BG too (don't regenerate it globaly, but instead clear the 12x12 = 144 pixels we modified :)
                hitmask.erase( self.maskhole, (int(self.x-6), int(self.y-6)))
                
                #Desactivate us
                self.setOff()
            
            #If we are out of bounds, kill us too!
            if self.isActive() == True and (self.y > 300 or self.x < 0 or self.x > 320 or self.y < 0):
                #Desactivate us
                self.setOff()
         
    
    # Draw the bullet on the specified surface
    # Param ( surface to draw into)
    def render( self, display ):    
        pygame.draw.rect(display, (255,255,255,255), (self.x-2, self.y-2, 4, 4) )
        