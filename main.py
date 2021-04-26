"""
                MINIGUN MINER
                
            A Python game for the Ludum Dare 48th edition
                        by Dr. Ludos (2021)
            
            This tiny and very barebone game was made from scratch in about 10h, as a way to discover the pygame library :)

            Get all my other games: 
                http://drludos.itch.io/
            Support my work and get access to betas and prototypes:
                http://www.patreon.com/drludos

"""

import pygame
import sys
import os
import math
import random

from bullet import Bullet
from gold import Gold

from pygame.locals import *


# === INIT ===

#Init pygame mixer for audio playing 
# We do it BEFORE the pygame.init to avoid a delay/latency when playing audio (thanks https://stackoverflow.com/questions/18273722/pygame-sound-delay/36366595)
pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.mixer.init()

#Set up pygame
pygame.init()

#Set up the display (windowed)
gameDisplay = pygame.display.set_mode((320, 240))
pygame.display.set_caption('Minigun Miner')

#Define pygame clock (to run the game at a constant fps)
clock = pygame.time.Clock()



# === ASSETS ===

# Detect whether we run from a frozen app (PyInstaller) or source (normal case), as it'll change where the data files are located (thanks: https://stackoverflow.com/questions/41204057/pygame-not-loading-png-after-making-exe-with-pyinstaller)
# If the code is frozen, use this path (the temp folder created by PyInstaller):
if getattr(sys, 'frozen', False):
    rootPath = sys._MEIPASS
# Else, we use the path the current file is currently running from
else:
    rootPath = os.path.dirname(__file__)

#Define the assets dir
assetsPath=os.path.join(rootPath, "assets")

# Player sprite
sprPlayerORIG = pygame.image.load( os.path.join(assetsPath, "player.png")).convert()
sprPlayerORIG.set_colorkey((255,0,255))
sprPlayer=pygame.transform.rotate(sprPlayerORIG, -90)
# Load the head sprite (non-rotated) separatedly
sprPlayerHEAD = pygame.image.load( os.path.join(assetsPath, "playerHEAD.png")).convert()
sprPlayerHEAD.set_colorkey((255,0,255))
# Load the player bitmask from another file (used for collision)
hitPlayer = pygame.image.load( os.path.join(assetsPath, "playerHIT.png"))
hitPlayer = pygame.mask.from_surface(hitPlayer)

# Background
sprBackground = pygame.image.load(os.path.join(assetsPath, "background.png")).convert()
colorDirt=(153,99,67, 255) #color used for dirt to dig into
colorVoid=(87,47,23, 255) #color used for the void that we can move into
#Generate a bitmask of the BG using the "dirt" color
hitBackground=pygame.mask.from_threshold(sprBackground, colorDirt, (1, 1, 1, 255))

#Load font
fontBig = pygame.font.SysFont("IMPACT", 48)
font = pygame.font.SysFont("IMPACT", 18)
# Text messages
#txtTitle = font.render("%d x %d" % (hitBackground.count(), hitPlayer.count()), False, (255,255,255))
txtTitle = fontBig.render("Minigun Miner", True, (255,255,255))
txtGameOver = fontBig.render("GAME OVER", True, (255,255,255))
txtScore = font.render("SCORE: 0", True, (255,255,255))
txtHowtoA = font.render("AIM: Left/Right arrow", True, (255,255,255))
txtHowtoB = font.render("SHOOT+MOVE: Space", True, (255,255,255))
txtHowtoC = font.render("FULLSCREEN ON/OFF: F", True, (255,255,255))
txtHowto2 = font.render("PRESS SPACE TO START or ESC to quit", True, (255,255,255))
txtHighscore = font.render("NEW HIGHSCORE!", True, (255,255,255))

#Audio files
sfxShoot=pygame.mixer.Sound(os.path.join(assetsPath, "shoot.wav"))
sfxGold=pygame.mixer.Sound(os.path.join(assetsPath, "gold.wav"))
sfxGameOver=pygame.mixer.Sound(os.path.join(assetsPath, "gameover.wav"))



# === VARIABLES ===

# Program State (0: title / 1: gameplay / 2: gameover)
STATE=0

#Bullet container list
bullets=[]

#Gold nugget container list
golds=[]

#Highscore
highscore=0

# ============================
# ======== FUNCTIONS ==========
# ============================

# This function init the game state (and defines the gameplay variable along the way!)
def initGame():
    
    #Reset Player vars

    global playerX
    playerX=160
    global playerY
    playerY=75
    global speedX
    speedX=0
    global speedY
    speedY=0
    global angle
    angle=-90
    #Time to wait before being able to fire a new bullet
    global cooldown
    cooldown=3
    
    #Reset score
    global score
    score=0
    global txtScore
    txtScore = font.render("SCORE: %d" % (score), True, (255,255,255))
    
    #Reset player sprite
    global sprPlayer
    sprPlayer=pygame.transform.rotate(sprPlayerORIG, -90)

    #Reset background (and its bitmask)
    global sprBackground
    sprBackground = pygame.image.load(os.path.join(assetsPath, "background.png")).convert()
    global hitBackground
    hitBackground=pygame.mask.from_threshold(sprBackground, colorDirt, (1, 1, 1, 255))
    
    #Desactivate all the already created bullets
    for bullet in bullets:
        bullet.setOff()
    
    #Desactivate all the already created bullets
    for gold in golds:
        gold.setOff()    

    golds.append( Gold( playerX, playerY+120))

# This function scroll down the background (infinitively generated as full of dirt to dig into)
def scrollBG(scrollY):
    
    #First, convert the scrollY value as integer because we are doing pixel operation, where the float has no mean
    scrollY=int(math.ceil(scrollY))
    
    # DISABLED, as it was not fun after all
    #Increase score
    #global score
    #score += scrollY
    #global txtScore
    #txtScore = font.render("SCORE: %d" % (score), False, (255,255,255))
    
    #Scroll the background image as requested (move it up!)
    sprBackground.scroll(0, -scrollY)
    
    #Scroll the gold nuggets too
    for gold in golds:
        if gold.isActive():
            gold.move(0,-scrollY)
    
    #And then draw a rectangle full of "dirt" at the bottom of the image to replace the empty area left over by the previous scrolling
    pygame.draw.rect(sprBackground, colorDirt, (0,320-scrollY,320,scrollY))
    
    #generate a new gold nugget randomly
    if random.randrange(40) == 0:
        golds.append( Gold(random.randrange(20, 280), 280) )
    
    #Update the bitmask of the BG
    global hitBackground
    hitBackground=pygame.mask.from_threshold(sprBackground, colorDirt, (1, 1, 1, 255))


# ============================
# ======== MAIN LOOP ==========
# ============================

#Init the game at startup
initGame()

#main loop
while True: 
    
    
    # === GAMEPLAY ===
    if STATE == 1:
        
        
        # -= PLAYER CONTROL =-
        
        # Rotate left
        if pygame.key.get_pressed()[pygame.K_LEFT]:
            # Change angle
            angle -= 5
            # Generate a new rotated player sprite image from the source (to avoid corrupting it with all the rotations over time)
            sprPlayer = pygame.transform.rotate(sprPlayerORIG, angle)
            # And copy the non-rotated head over it
        # Rotate right    
        elif pygame.key.get_pressed()[pygame.K_RIGHT]:
            # Change angle
            angle += 5    
            # Generate a new rotated player sprite image from the source (to avoid corrupting it with all the rotations over time)
            sprPlayer = pygame.transform.rotate(sprPlayerORIG, angle)
        
        
        
        # SHOOT / THRUST
        if pygame.key.get_pressed()[pygame.K_SPACE]:
            
            # Move the player with the recoil from it's minigun!
            speedX -= 0.05*math.cos(math.radians(angle))
            #The player can't move downard with this recoil (not realistic, but more fun!)
            speedY += min(0, 0.1*math.sin(math.radians(angle)) )
            
            # If the cooldown timer isn't over
            if cooldown > 0 :
                #wait before being able to fire again!
                cooldown -= 1
            
            #Else, we can shoot a bullet!   
            else:
                
                #We'll only fire once per cooldown
                fired=False
                
                #First, we'll see if we can recycle one of the previous bullet created in the list
                for bullet in bullets:
                    #If this bullet is inactive
                    if not fired and bullet.isActive() == False:
                        
                        #Recycle it with new params
                        bullet.setup( playerX+(16*math.cos(math.radians(angle))), playerY-(16*math.sin(math.radians(angle))), 4, -angle+9-random.randrange(19) )
                        
                        #And activate it!
                        bullet.setOn()
                        
                        #Mark us a "fired" to avoid creating a new bullet
                        fired=True
                        
                # If we still haven't fired because no previous bullet was inactive, we create a new one!
                if fired == False:
                    
                    #Create a new bullet and add it to the list!
                    bullets.append( Bullet( playerX+(16*math.cos(math.radians(angle))), playerY-(16*math.sin(math.radians(angle))), 4, -angle+9-random.randrange(19))  )
                    
                    #Mark us a "fired" just in case
                    fired=True
        
                #In any case, set the cooldown to avoid firing too much bullets!
                cooldown=1
        
                #Play SFX                
                sfxShoot.play()
                
        
        
        # -= X MOVEMENT =-
        
        #Ooh, decay
        speedX *= 0.98
        
        # Move Player
        playerX += speedX
        
        # Player stay inside bounds
        if playerX < 16:
            playerX = 16
            speedX = 0
        elif playerX > 304:
            playerX = 304
            speedX = 0
        
        
        # -= Y MOVEMENT =-
        
        #Ooh, gravity!
        speedY += 0.03
    
        #Cap the Y speed in the downward direction (for the upward direction, there is a screen boundary)
        if speedY > 4:
            speedY = 4
    
        # if the player is high enough in the screen or moving up while in the "scroll instead of moving" area
        if (playerY < 120) or (playerY >= 120 and speedY < 0):
           
           #then move the player itself
            playerY += speedY

            # Player stay inside bounds
            if playerY < 10:
                playerY = 10
                speedY = 0
        # Else, scroll the screen    
        else:
            
            # Scroll the BG down using player speed
            scrollBG( speedY )
            
            # and for the player position at the boundary
            playerY = 120
    
    
    
        # -= BULLET MOVEMENT =-
        
        # Make all the active bullets move (and create holes if needed!)
        for bullet in bullets:
            if bullet.isActive() == True :
                bullet.move( sprBackground, hitBackground, colorVoid )
        
        
        # -= PLAYER COLLISION WITH GOLDS =-
        
        #Compute the player rect
        playerRect=Rect( playerX-10, playerY-10, 20, 20)
        
        # Check if the player has collected any of the gold!
        for gold in golds:
            if gold.isActive():
                
                #Use the internal function of the gold to check whether they are collected or not
                if gold.isCollected(playerRect):
                
                    #Increase score!
                    score += 1
                    txtScore = font.render("SCORE: %d" % (score), True, (255,255,255))
                    
                    #Play SFX                
                    sfxGold.play()
        
        
        # -= PLAYER COLLISION WITH BG =-
        
        # if the playerbitmask collides with the BG bitmask
        #if hitBackground.overlap(hitPlayer, (int(playerX-int((sprPlayer.get_width()/2))), int(playerY-int((sprPlayer.get_height()/2)))) ):
        if hitBackground.overlap_area(hitPlayer, (int(playerX-int((sprPlayer.get_width()/2))), int(playerY-int((sprPlayer.get_height()/2)))) ) > 40 :
            
            #Game over, man!
            STATE=2
            
            #Dig a big hole in the backgroud (as we exploded!)
            pygame.draw.circle( sprBackground, colorVoid, (int(playerX), int(playerY)), 32)
            
            #Define a cooldown timer so we don't restart immediatedly (re-use the firing cooldown var)
            cooldown=60
            
            #Did we make a highscore?
            if score > highscore:
                txtHighscore = font.render("NEW HIGHSCORE!", True, (255,255,255))
                highscore=score
            #else, display the current highscore
            else:
                txtHighscore = font.render("HIGHSCORE: %d" % (score), True, (255,255,255))
            
            #Play SFX            
            sfxShoot.stop()            
            sfxGameOver.play()
        
        
        
        
        # -= RENDER SCREEN =-
        
        # Draw Background
        gameDisplay.blit(sprBackground, (0, 0))
        
        # Draw active bullets
        for bullet in bullets:
            if bullet.isActive():
                bullet.render( gameDisplay )
        
        #Draw active nuggets
        for gold in golds:
            if gold.isActive():
                gold.render( gameDisplay )
        
        # Draw player (rotated sprite centered on current player coordinates)
        gameDisplay.blit(sprPlayer, (playerX-int((sprPlayer.get_width()/2)), playerY-int((sprPlayer.get_height()/2))) )
        #Draw its non-rotated head too!
        gameDisplay.blit(sprPlayerHEAD, (playerX-int((sprPlayerHEAD.get_width()/2)), playerY-int((sprPlayerHEAD.get_height()/2))) )
        
        # Display score
        gameDisplay.blit( txtScore, ( 320-(txtScore.get_width()+4) , 0))
        
        # Redraw the whole screen
        pygame.display.flip()
    
    
    
    
    
    
    # === GAME OVER ===
    elif STATE == 2:
        
        # -= RENDER SCREEN =-
        
        # Draw Background
        gameDisplay.blit(sprBackground, (0, 0))
        
        #Draw active nuggets
        for gold in golds:
            if gold.isActive():
                gold.render( gameDisplay )
        
        #Display message
        if cooldown < 20:
            gameDisplay.blit(txtGameOver, (160-(txtGameOver.get_width()/2), 20))

        #Display highscore message
        if cooldown < 10:
            gameDisplay.blit(txtHighscore, (160-(txtHighscore.get_width()/2), 80))

        #Display other message
        if cooldown == 0:
            gameDisplay.blit(txtHowtoC, (160-(txtHowtoC.get_width()/2), 190))
            gameDisplay.blit(txtHowto2, (160-(txtHowto2.get_width()/2), 210))

        # Display score
        gameDisplay.blit( txtScore, ( 320-(txtScore.get_width()+4) , 0))        
        
        #Redraw the whole screen
        pygame.display.flip()
        
        # -= PLAYER CONTROL =-
        
        # If the cooldown time isn't finished
        if cooldown > 0:
            # decrease coutdown so player can see that the game is over before being able to restart game
            cooldown -= 1
        
        # Restart when key pressed
        elif pygame.key.get_pressed()[pygame.K_SPACE]:
            
            # Reset game state
            initGame()
            
             #Redraw the whole screen
            pygame.display.flip()
            
            # And set the program to gameplay state
            STATE=1
    
    
    
    
    
    
    # === TITLE SCREEN ===
    elif STATE == 0:
        
        # -= RENDER SCREEN =-
        
        # Draw Background
        gameDisplay.blit(sprBackground, (0, 0))
        
        #Display message
        gameDisplay.blit(txtTitle, (160-(txtTitle.get_width()/2), 2))
        
        #Display how to play!
        gameDisplay.blit(txtHowtoA, (160-(txtHowtoA.get_width()/2), 100))
        gameDisplay.blit(txtHowtoB, (160-(txtHowtoA.get_width()/2), 120))
        gameDisplay.blit(txtHowtoC, (160-(txtHowtoA.get_width()/2), 160))
        gameDisplay.blit(txtHowto2, (160-(txtHowto2.get_width()/2), 210))
        
        #draw player (rotated sprite centered on current player coordinates)
        gameDisplay.blit(sprPlayer, (playerX-int((sprPlayer.get_width()/2)), playerY-int((sprPlayer.get_height()/2))))
        #Draw its non-rotated head too!
        gameDisplay.blit(sprPlayerHEAD, (playerX-int((sprPlayerHEAD.get_width()/2)), playerY-int((sprPlayerHEAD.get_height()/2))) )
        
        #Draw active nuggets
        for gold in golds:
            if gold.isActive():
                gold.render( gameDisplay )
        
        #Redraw the whole screen
        pygame.display.flip()
        
        
        # Start when key pressed
        if pygame.key.get_pressed()[pygame.K_SPACE]:
            
            # Reset game state
            initGame()
            
            # And set the program to gameplay state
            STATE=1
    
    
    
    
    # === MISC ===
    # Quit Game when requested
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
         #Allow to toggle windowed / fullscreen mode with a key    
        if (event.type is KEYDOWN and event.key == K_f):
            if gameDisplay.get_flags() & FULLSCREEN:
                pygame.display.set_mode((320,240))
            else:
                pygame.display.set_mode((320,240), FULLSCREEN)        
    #Also quits when ESC key is pressed
    if pygame.key.get_pressed()[pygame.K_ESCAPE]: 
        pygame.quit()
        sys.exit()
        
   
            
    # === BACKEND ===
    
    # Run at 60 fps
    clock.tick(60)
