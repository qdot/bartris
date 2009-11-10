#!/usr/bin/env python
"""
    Python Tetris is a clunky pygame Tetris clone. Feel free to make it better!!
    Copyright (C) 2008 Nick Crafford <nickcrafford@earthlink.net>

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""
import serial
import pygame, time, random, os
from Tetromino     import *
from Grid          import *
from Sound         import *
from pygame.locals import *
from math          import *
 
#Initialize Vars :)

num_cells_wide      = 10
num_cells_high      = 20
cell_width          = 25
cell_height         = 25
black               = (0,0,0)
white               = (255,255,255)
blue                = (0,0,255)
red                 = (255,0,0)
grey                = (171,171,171)
darkGrey            = (85,85,85)
brown               = (0x8e, 0x48, 0x1d)
color_dict          = {2: blue, 6 : brown, 10: white}
color_range         = 10
starting_cell_x     = 4
starting_cell_y     = 1
last_falling_time   = 0
last_moving_time    = 0
last_rotating_time  = 0
level_up_line_count = 3
lastNumLinesCleared = 0
topY                = 0
timesFound          = 0
current_level       = 1
fallingRate         = .0005
movingRate          = [0.00005,.00004,0.00003,0.00002,0.00001]
rotatingRate        = [0.00009,0.00008,0.00007,0.00006,0.00005]
currentY            = 0
textBuff            = 2
rateIncrease        = .00015
grid                = Grid(1,1,cell_width,cell_height,num_cells_wide,num_cells_high,black)
gameOver            = False
tetrominoList       = ['T','I','O','S','Z','L','J']
levels              = [0.0004,0.00025,0.0001,0.00005,0.00002]
tetromino           = Tetromino(starting_cell_x,starting_cell_y,black,brown,tetrominoList[0])
sound               = Sound()

#Init Pygame
os.environ['SDL_VIDEO_CENTERED'] = '1'
pygame.init()
screen = pygame.display.set_mode((grid.width+textBuff,grid.height+textBuff),0,32)
pygame.display.set_caption("Python Tetris")
#Initialize Fonts
if pygame.font:
    font = pygame.font.Font(None, 18)

#Main Game Loop

while True:
    time.sleep(0.01)   
    key  = ''
    for event in pygame.event.get():
        if event.type == QUIT:
            break
        if event.type == pygame.KEYDOWN: 
            key = event.key
        
    #Grab vars
    rand          = random.randint(0,len(tetrominoList)-1)            
    current_time  = time.time()/1000.0
    falling_time  = current_time - last_falling_time
    move_down_ok  = tetromino.max_y < grid.height            
    move_left_ok  = tetromino.min_x > 0
    move_right_ok = tetromino.max_x < grid.width
    
    #Render Text
    if not gameOver:
        if tetromino.active:
            if key == K_RIGHT and move_right_ok:
                tetromino.move(grid,1,0)
            if key == K_LEFT and move_left_ok:
                tetromino.move(grid,-1,0)
            if key == K_DOWN and move_down_ok:
                tetromino.move(grid,0,1)
                currentY += 1
            if key == K_UP and move_right_ok and move_left_ok and move_down_ok:
                tetromino.rotate(grid)            
            #ADDED: quit key
            if key == K_q:
                break;            

            #Downward fall
            if falling_time >= fallingRate and move_down_ok:
                last_falling_time = current_time            
                tetromino.move(grid,0,1)
                currentY += 1
            if not move_down_ok:
                tetromino.cluck.play()
                tetromino.active = False        
        
        else: #New Tetromino
            #ADDED: Set tetromino color to one of our three allowed colors
            color_index = random.randint(0,color_range)
            print color_index
            color = ()
            print sorted(color_dict.keys())
            print sorted(color_dict)
            for color_probability in sorted(color_dict.keys()):                
                if color_index <= color_probability:
                    color = color_dict[color_probability]
                    break

            tetromino = Tetromino(starting_cell_x,starting_cell_y,black,color,tetrominoList[rand])

            grid.checkForLines()
            #Test for GAME OVER
            topY = grid.topY()
            if topY <= 2:
                timesFound += 1
            if timesFound > 3:
                gameOver = True
        #Levels and Speedup
        if grid.numLinesCleared % level_up_line_count == 0 and lastNumLinesCleared != grid.numLinesCleared:
            lastNumLinesCleared = grid.numLinesCleared
            if current_level < len(levels):
                fallingRate = levels[current_level]
            current_level += 1
            sound.play("../sound/levelup.wav")
            #ADDED: Color accumulation output and reset on level finish
            print grid.color_accum
            grid.color_accum = {}

        #Render Background
        pygame.draw.rect(screen,(255,255,255),Rect(0,0,grid.width+2,grid.height+2))            
        #Render Grid
        grid.render(screen)
        lineText       = "Lines: " + str(grid.numLinesCleared) + "  Level: " + str(current_level)
        lines_text     = font.render(lineText, 1, white)
        lines_text_pos = Rect((1,1),(300,20))
        screen.blit(lines_text, lines_text_pos)            
    else:
        #Render Background
        pygame.draw.rect(screen,(255,255,255),Rect(0,0,grid.width+2,grid.height+2))
        #Render Grid
        grid.render(screen)
        game_over_text     = font.render("GAME OVER... LEVEL: "+str(current_level)+" LINES: " + str(grid.numLinesCleared),1, red)
        game_over_text_pos = Rect((1,1),(300,20))
        screen.blit(game_over_text,game_over_text_pos)  
    #Update Display
    pygame.display.update()
