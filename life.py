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

import pygame, sys, math, random, time
from pygame.locals import *

# main program config
debug = True
paused = True
mute = False
res = (1366, 768) # resolution
borderWidth = 10
bottomPad = 2
fps = 60
title = 'life'
timeInc = 0.1            # seconds to wait each iteration
globalTime = 0         # global time counter

# player startup values
startingPoints = 0
startingLives = 5


# game data
minNeighborsToLive = 2
maxNeighborsToLive = 3
neighborsToStart = 3

player = None


# color presets
red = pygame.Color(255,0,0)
green = pygame.Color(0,255,0)
darkGreen = pygame.Color(0,140,0)
blue = pygame.Color(0,0,255)
lightBlue = pygame.Color(200,200,255)
white = pygame.Color(255,255,255)
black = pygame.Color(0,0,0)

def gray (val):
    return pygame.Color(val,val,val)

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
        
class Block:
    
    size = 15            # length of side    
    fillColor = white
    borderColor = black
    
    def __init__(self, col):
        self.fillColor = col
    
    def getSize(self):
        return self.size
        
    def getFillColor(self):
        return self.fillColor
        
    def setFillColor(self, newF):
        self.fillColor = newF
     
    def getBorderColor(self):
        return self.borderColor
    
    def setBorderColor(self, newB):
        self.borderColor = newB
    
    def draw(self, wso, x, y):    
        pygame.draw.rect(wso, self.getFillColor(), (x,y,self.size,self.size), 0)
        pygame.draw.rect(wso, self.getBorderColor(), (x,y,self.size,self.size), 1)
                
class Cell:
    
    size = 1
    alive = False
    aliveGraphic = None
    deadGraphic = None
    
    def __init__(self, gAlive, gDead):
        self.aliveGraphic = gAlive
        self.deadGraphic = gDead
    
    def setAlive(self, newStatus):
        self.alive = newStatus
        
    def kill(self):
        self.alive = False
        
    def start(self):
        self.alive = True
        
    def toggleAlive(self):
        self.alive = not self.alive
        
    def isAlive(self):
        return self.alive
        
    def getGraphic(self):
        if self.alive:
            return self.aliveGraphic
        else:
            return self.deadGraphic
       
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


# playing grid
gridWidth = int(math.floor((res[0] - borderWidth*2)/Block(white).getSize()))
gridHeight = int(math.floor((res[1] - borderWidth*5)/Block(white).getSize()))

# init 
grid = []

for x in range(gridHeight):
    grid.append([])
    for y in range(gridWidth):
        grid[x].append(Cell(Block(darkGreen), Block(white)))
        
        
random.seed()
for row in grid:
    for el in row:
        if (random.choice([True, False, False, False, False])): # , False, False, False, False])):
            el.toggleAlive()
        
        
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
    
    # draw grid
    drawGrid(windowSurfObj, grid)
    

    # debug status
    if debug:
        drawText(windowSurfObj, 'Status: ', (borderWidth, res[1] - (fontSize)))
    else:
        drawText(windowSurfObj, 'Lives: ' + str(player.getLives()), (borderWidth, res[1] - (fontSize)))
        
    # stats
    drawText(windowSurfObj, 'Generation: ' + str(globalTime), (res[0]*3/5 , res[1] - (fontSize)))
    drawText(windowSurfObj, 'Level: ' + str(game.getLevel()), (res[0]*4/5 , res[1] - (fontSize)))

def drawGrid(wso, g):
    gridX, gridY = res[0]/2 - Block(white).getSize()*gridWidth/2, res[1]/2 - Block(white).getSize()*gridHeight/2 - fontSize/2
    
    for row in grid:
        for el in row:
            el.getGraphic().draw(wso, gridX + row.index(el)*el.getGraphic().getSize(), gridY + grid.index(row)*el.getGraphic().getSize() )   


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

def iterate():
    global globalTime
    #time.sleep(timeInc)
    globalTime += 1
    
    evaluate()
    
def evaluate():
    global grid

    # not looking at any edges
    for row in range(len(grid)):
        for col in range(len(grid[row])):
            neighbors = getLiveNeighbors(grid, row, col)
            if (grid[row][col].isAlive()):                                                   # live cells
                if (neighbors < minNeighborsToLive or neighbors > maxNeighborsToLive):   #   -- kill criteria
                    grid[row][col].kill()
            else:                                                                        # dead cells
                if (neighbors == neighborsToStart):                                      #   -- birth criteria
                    grid[row][col].start()
                    
def getLiveNeighbors(g, r, c):                # grid, row, column
    neighbors = 0    
    
    if (r == 0):                              # top edge
        if (c == 0):                          # top left corner
            if (g[r][c+1].isAlive()):
                neighbors += 1
            if (g[r+1][c+1].isAlive()):
                neighbors += 1
            if (g[r+1][c].isAlive()):
                neighbors += 1
                
        elif (c == len(g[r]) - 1):               # top right corner
            if (g[r][c-1].isAlive()):
                neighbors += 1
            if (g[r+1][c-1].isAlive()):
                neighbors += 1
            if (g[r+1][c].isAlive()):
                neighbors += 1
                
        else:
            if (g[r][c-1].isAlive()):
                neighbors += 1
            if (g[r][c+1].isAlive()):
                neighbors += 1
                
            if (g[r+1][c-1].isAlive()):
                neighbors += 1
            if (g[r+1][c].isAlive()):
                neighbors += 1
            if (g[r+1][c+1].isAlive()):
                neighbors += 1 
        
    elif (r == len(g) - 1):                   # bottom edge
        if (c == 0):                          # bottom left corner
            if (g[r-1][c].isAlive()):
                neighbors += 1
            if (g[r-1][c+1].isAlive()):
                neighbors += 1
            if (g[r][c+1].isAlive()):
                neighbors += 1
                
        elif (c == len(g[r]) - 1):               # bottom right corner
            if (g[r-1][c].isAlive()):
                neighbors += 1
            if (g[r-1][c-1].isAlive()):
                neighbors += 1
            if (g[r][c-1].isAlive()):
                neighbors += 1
                
        else:
            if (g[r][c-1].isAlive()):
                neighbors += 1
            if (g[r][c+1].isAlive()):
                neighbors += 1
                
            if (g[r-1][c-1].isAlive()):
                neighbors += 1
            if (g[r-1][c].isAlive()):
                neighbors += 1
            if (g[r-1][c+1].isAlive()):
                neighbors += 1 
        
    elif (c == 0):                            # left edge
        if (g[r-1][c].isAlive()):
            neighbors += 1
        if (g[r+1][c].isAlive()):
            neighbors += 1
            
        if (g[r-1][c+1].isAlive()):
            neighbors += 1
        if (g[r][c+1].isAlive()):
            neighbors += 1
        if (g[r+1][c+1].isAlive()):
            neighbors += 1 
        
        
    elif (c == len(g[r]) - 1):                # right edge
        if (g[r-1][c-1].isAlive()):
            neighbors += 1
        if (g[r][c-1].isAlive()):
            neighbors += 1
        if (g[r+1][c-1].isAlive()):
            neighbors += 1
            
        if (g[r-1][c].isAlive()):
            neighbors += 1
        if (g[r+1][c].isAlive()):
            neighbors += 1
        
    else:                                     # all those not on the edge
        if (g[r-1][c-1].isAlive()):
            neighbors += 1
        if (g[r][c-1].isAlive()):
            neighbors += 1
        if (g[r+1][c-1].isAlive()):
            neighbors += 1
        
        if (g[r-1][c].isAlive()):
            neighbors += 1
        if (g[r+1][c].isAlive()):
            neighbors += 1
            
        if (g[r-1][c+1].isAlive()):
            neighbors += 1
        if (g[r][c+1].isAlive()):
            neighbors += 1
        if (g[r+1][c+1].isAlive()):
            neighbors += 1    
            
        
    return neighbors

# main program loop
while True:

    # check status, lives, bricks, etc
    checkGame()
    
    # do AI
    if not paused:
        iterate()
    
    # draw
    draw()
    
    # input
    processInput()
    pollInputs()

    # update draw
    pygame.display.update()
    fpsClock.tick(fps)
    
    

