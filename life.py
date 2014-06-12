# life.py - life is a pygame implementation of something like Conway's Game of Life
# Author: nitor
# Date: Jun 2014
#
#########################
#
# MIT/Expat License
#
# Copyright (C) 2014 K. Brett Mulligan
#
# Permission is hereby granted, free of charge, to any person obtaining a copy 
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights 
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell 
# copies of the Software, and to permit persons to whom the Software is 
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in 
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
#########################

import pygame, sys, math, random
from pygame.locals import *

# main program config
debug = True
paused = True
mute = False
res = (1366, 768) # resolution
borderWidth = 10
bottomPad = 2
fps = 60
title = 'chairflyer'
timeInc = 3 # seconds

waypointsFilename = "waypoints.txt"


# player startup values
startingPoints = 0
startingLives = 5

# color presets
red = pygame.Color(255,0,0)
green = pygame.Color(0,255,0)
blue = pygame.Color(0,0,255)
lightBlue = pygame.Color(200,200,255)
white = pygame.Color(255,255,255)
black = pygame.Color(0,0,0)

def gray (val):
    return pygame.Color(val,val,val)
    
def recip (heading):
    return (heading + 180) % 360 

def distance (a, b):
    return math.sqrt(abs(a[0] - b[0])**2 + abs(a[1] - b[1])**2)
    
# Class defs
class Player:

    def __init__(self, pts, level):

        self.pts = pts
        self.level = level

    pts = 0
    level = 0
    lives = startingLives

    def getPoints(self):
        return self.pts

    def addPoints(self, newPoints):
        self.pts += newPoints

    def setPoints(self, newPoints):
        self.pts = newPoints

    def takeLife(self):
        self.lives -= 1

    def setLives(self, newLives):
        self.lives = newLives

    def getLives(self):
        return self.lives

    def addLife(self):
        self.lives += 1
    
class Game:

    level = 0

    def __init__(self):
        level = 1

    def setLevel(self, lvl):
        self.level = lvl

    def getLevel(self):
        return self.level
        
        
# setup

pygame.init()
fpsClock = pygame.time.Clock()

windowSurfObj = pygame.display.set_mode(res, pygame.FULLSCREEN)
pygame.display.set_caption(title)


fontSize = 24
fontObj = pygame.font.Font(None, fontSize)
label = 'Status: '
msg = 'Program started...'

# top level game state
game = Game()
game.setLevel(1)
player = Player(0,1)



# input section
def processInput():
    global paused, mute, msg, debug
    
    global lead
    
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        
        elif event.type == MOUSEMOTION:
            if not paused:
                pass
        elif event.type == MOUSEBUTTONUP:
            if event.button == 1:
                leftClick(event.pos)
            elif event.button == 2:
                middleClick(event.pos)
            elif event.button == 3:
                rightClick(event.pos)
            elif event.button == 4:
                scrollUp()
            elif event.button == 5:
                scrollDown()
                
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pygame.event.post(pygame.event.Event(QUIT))
            elif event.key == K_p:
                paused = not paused
            elif event.key == K_n:
                nextLevel()
            elif event.key == K_d:
                debug = not debug
            elif event.key == K_m or event.key == K_s:
                mute = not mute
            elif event.key == K_SPACE:
                togglePause()

def pollInputs():

    keys = pygame.key.get_pressed()
    if keys[K_LEFT]:
        if not paused:
            keyLeft()
    elif keys[K_RIGHT]:
        if not paused:
            keyRight()
    if keys[K_UP]:
        if not paused:
            keyUp()     
    elif keys[K_DOWN]:
        if not paused:
            keyDown()

def leftClick(pos):
    global msg, lead
    msg = 'left click'

def rightClick(pos):
    global msg
    msg = 'right click'

def middleClick(pos):
    global msg
    msg = 'middle click'  

def scrollUp():
    global msg, lead
    msg = 'scroll up'
    
def scrollDown():
    global msg, lead
    msg = 'scroll down'
    
def keyLeft():
    global msg, lead
    msg = 'key left'
    
def keyRight():
    global msg, lead
    msg = 'key right'
    
def keyUp():
    global msg, lead
    msg = 'key up'
    
def keyDown():
    global msg, lead
    msg = 'key down'
       
def togglePause():
    global paused
    paused = not paused
    
# graphics    
def draw():
    windowSurfObj.fill(black)

    # draw background
    drawBackground(windowSurfObj)
    
    # draw border
    pygame.draw.rect(windowSurfObj, white, (borderWidth,borderWidth,res[0]-borderWidth*2,res[1]-(fontSize + bottomPad + borderWidth*2)), 1)
    
    
    # debug status
    if debug:
        drawText(windowSurfObj, 'Status: ', (borderWidth, res[1] - (fontSize)))
    else:
        drawText(windowSurfObj, 'Lives: ' + str(player.getLives()), (borderWidth, res[1] - (fontSize)))
        
    # stats
    drawText(windowSurfObj, 'Score: ' + str(player.getPoints()), (res[0]*3/5 , res[1] - (fontSize)))
    drawText(windowSurfObj, 'Level: ' + str(game.getLevel()), (res[0]*4/5 , res[1] - (fontSize)))

def drawBackground(wso):
    pygame.draw.circle(wso, gray(25), (res[0]/3 + 40, res[1]/3), 240)
    pygame.draw.circle(wso, gray(20), (res[0]*2/3, res[1]*2/3), 250)
    pygame.draw.circle(wso, gray(15), (res[0]*1/4, res[1]*4/5), 200)

def drawText(wso, string, coords):
    textSurfObj = fontObj.render(string, False, white)
    textRectObj = textSurfObj.get_rect()
    textRectObj.topleft = coords
    wso.blit(textSurfObj, textRectObj)

def checkGame():
    if player.getLives() <= 0:
        resetGame()
    
def nextLevel():
    global game

    game.setLevel(game.getLevel() + 1)

    if not paused:
        togglePause()

def resetGame():
    global game, player
    
    game.setLevel(1)
    
    if not paused:
        togglePause()
    
    player.setPoints(startingPoints)
    player.setLives(startingLives)

# main program loop
while True:

    # check status, lives, bricks, etc
    checkGame()
    
    # do AI
    
    # draw
    draw()
    
    # input
    processInput()
    pollInputs()

    # update draw
    pygame.display.update()
    fpsClock.tick(fps)

