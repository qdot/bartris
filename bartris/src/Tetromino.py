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
import random
import pygame
from pygame.locals import *

class Tetromino(object):
    def __init__(self,first_x,first_y,mask_color,color, t):
        self.first_x         = first_x
        self.first_y         = first_y
        self.color           = color
        self.mask_color      = mask_color
        self.positions       = []
        self.max_x           = 0
        self.min_x           = 0
        self.max_y           = 0
        self.currentPosition = 0
        self.oldPosition     = 0
        self.active          = True
        self.id              = random.random()
        self.volume          = 1.0
        self.mfile           = '../sound/cluck.wav'
        self.freq            = 44100
        self.bitsize         = 8
        self.channels        = 1
        self.buffer          = 4096
        #Tetromino Switch Statement
        if t == 'I':
            self.I()
        elif t == 'O':
            self.O()
        elif t == 'T':
            self.T()
        elif t == 'S':
            self.S()
        elif t == 'Z':
            self.Z()
        elif t == 'L':
            self.L()
        elif t == 'J':
            self.J()
        #Initialize Sound
        if pygame.mixer:
            pygame.mixer.init(self.freq, self.bitsize, self.channels, self.buffer)
            pygame.mixer.music.set_volume(self.volume)
        self.cluck = pygame.mixer.Sound(self.mfile)
            
    def move(self, grid, x_direction, y_direction):
        self.max_x = 0
        self.min_x = 0
        self.max_y = 0        
        max_x_pos  = 0
        min_x_pos  = 50
        max_y_pos  = 0
        if self.active:
            #Render Current Position in color
            if grid.accept(self.id,self.positions[self.currentPosition],x_direction,y_direction):
                #Set all to mask color
                pos = self.positions[self.currentPosition]
                for idx in range(len(pos)):
                    grid.set(self.mask_color,pos[idx][0],pos[idx][1],0)
                for posIdx in range(len(self.positions)):
                    pos  = self.positions[posIdx]
                    for idx in range(len(pos)):                
                        pos[idx] = (pos[idx][0]+x_direction,pos[idx][1]+y_direction)
                        x        = pos[idx][0]
                        y        = pos[idx][1]
                        if posIdx == self.currentPosition:
                            grid.set(self.color,x,y,self.id)
                            if y > max_y_pos:
                                max_y_pos = y
                            if x > max_x_pos:
                                max_x_pos = x
                            if x < min_x_pos:
                                min_x_pos = x
                self.max_x = max_x_pos*grid.cell_width  + grid.cell_width
                self.min_x = min_x_pos*grid.cell_width 
                self.max_y = max_y_pos*grid.cell_height + grid.cell_height
            else:
                self.cluck.play()
                self.active = False
                
    def rotate(self,grid):
        self.max_y = 0
        if self.active:
            self.oldPosition = self.currentPosition
            pos = self.positions[self.oldPosition]
            for idx in range(len(pos)):
                grid.set(self.mask_color,pos[idx][0],pos[idx][1],0)                                
            if self.currentPosition < len(self.positions)-1:
                self.currentPosition += 1                
            else:
                self.currentPosition = 0
            self.move(grid,0,0)
            
    def I(self):
        #self.color = (49,199,239)
        self.positions.append([(self.first_x,   self.first_y),   (self.first_x+1, self.first_y),
                               (self.first_x+2, self.first_y),   (self.first_x+3, self.first_y)])
        self.positions.append([(self.first_x+2, self.first_y-2), (self.first_x+2, self.first_y-1),
                               (self.first_x+2, self.first_y),   (self.first_x+2, self.first_y+1)])
    def O(self):
        #self.color = (247,211,8)        
        self.positions.append([(self.first_x,   self.first_y),   (self.first_x+1, self.first_y-1),
                               (self.first_x+1, self.first_y),   (self.first_x,   self.first_y-1)])
    def T(self):
        #self.color = (173,77,156)        
        self.positions.append([(self.first_x,   self.first_y),   (self.first_x+1, self.first_y),
                               (self.first_x+2, self.first_y),   (self.first_x+1, self.first_y-1)])        
        self.positions.append([(self.first_x+1, self.first_y),   (self.first_x+2, self.first_y),
                               (self.first_x+1, self.first_y+1), (self.first_x+1, self.first_y-1)])           
        self.positions.append([(self.first_x,   self.first_y),   (self.first_x+1, self.first_y),
                               (self.first_x+2, self.first_y),   (self.first_x+1, self.first_y+1)])
        self.positions.append([(self.first_x+1, self.first_y),   (self.first_x,   self.first_y),
                               (self.first_x+1, self.first_y+1), (self.first_x+1, self.first_y-1)])
    def S(self):
        #self.color = (66,182,66)        
        self.positions.append([(self.first_x,   self.first_y),   (self.first_x+1, self.first_y),
                               (self.first_x+1, self.first_y+1), (self.first_x+2, self.first_y+1)])        
        self.positions.append([(self.first_x+2, self.first_y),   (self.first_x+2, self.first_y+1),
                               (self.first_x+1, self.first_y+1), (self.first_x+1, self.first_y+2)])
    def Z(self):        
        #self.color = (239,32,41)        
        self.positions.append([(self.first_x,   self.first_y+1), (self.first_x+1, self.first_y+1),
                               (self.first_x+1, self.first_y),   (self.first_x+2, self.first_y)])        
        self.positions.append([(self.first_x+1, self.first_y),   (self.first_x+1, self.first_y+1),
                               (self.first_x+2, self.first_y+1), (self.first_x+2, self.first_y+2)])
    def L(self):
        #self.color = (90,101,173)        
        self.positions.append([(self.first_x,   self.first_y),   (self.first_x,   self.first_y+1),
                               (self.first_x+1, self.first_y+1), (self.first_x+2, self.first_y+1)])        
        self.positions.append([(self.first_x+1, self.first_y),   (self.first_x+1, self.first_y+1),
                               (self.first_x,   self.first_y+2), (self.first_x+1, self.first_y+2)])
        self.positions.append([(self.first_x,   self.first_y+1), (self.first_x+1, self.first_y+1),
                               (self.first_x+2, self.first_y+1), (self.first_x+2, self.first_y+2)])
        self.positions.append([(self.first_x+2, self.first_y),   (self.first_x+1, self.first_y),
                               (self.first_x+1, self.first_y+1), (self.first_x+1, self.first_y+2)])
    def J(self):
        #self.color = (239,121,33)                
        self.positions.append([(self.first_x,   self.first_y+1), (self.first_x+1, self.first_y+1),
                               (self.first_x+2, self.first_y+1), (self.first_x+2, self.first_y)])
        self.positions.append([(self.first_x,   self.first_y),   (self.first_x+1, self.first_y),
                               (self.first_x+1, self.first_y+1), (self.first_x+1, self.first_y+2)])
        self.positions.append([(self.first_x,   self.first_y+1), (self.first_x,   self.first_y+2),
                               (self.first_x+1, self.first_y+1), (self.first_x+2, self.first_y+1)])
        self.positions.append([(self.first_x+1, self.first_y),   (self.first_x+1, self.first_y+1),
                               (self.first_x+1, self.first_y+2), (self.first_x+2, self.first_y+2)])            
