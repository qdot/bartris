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
import pygame,random
from   pygame.locals import *
from   Sound import *

class Grid(object):
    def __init__(self,start_x,start_y, cell_height,cell_width,num_cells_wide,num_cells_tall, color):
        self.cells           = {}
        self.start_x         = start_x
        self.start_y         = start_y
        self.cell_height     = cell_height
        self.cell_width      = cell_width
        self.num_cells_wide  = num_cells_wide
        self.num_cells_tall  = num_cells_tall
        self.numLinesCleared = 0
        self.color           = color
        self.height          = cell_height * num_cells_tall
        self.width           = cell_width  * num_cells_wide
        self.sound           = Sound()
        self.color_accum     = {}
        #Build Grid
        for x in range(self.num_cells_wide):
            for y in range(self.num_cells_tall):
                self.cells[(x,y)] = (color,Rect((x*self.cell_width+self.start_x,
                                                 y*self.cell_height+self.start_y),
                                                (self.cell_height,self.cell_width)),0)

    def set(self, color, x, y, id):
        self.cells[(x,y)] = (color,Rect((x*self.cell_width+self.start_x,
                                         y*self.cell_height+self.start_y),
                                        (self.cell_height,self.cell_width)),id)
    
    def render(self, screen):
        screen.lock()
        for key in self.cells:
            cell = self.cells[key]
            #BG Rect
            if cell[2] > 0:
                pygame.draw.rect(screen,(0,0,0),cell[1])
                rectLeft   = cell[1].left+1
                rectTop    = cell[1].top+1
                rectWidth  = cell[1].width-2
                rectHeight = cell[1].height-2
                nRect = Rect(rectLeft,rectTop,rectWidth,rectHeight)
                pygame.draw.rect(screen,cell[0],nRect)
            else:
                pygame.draw.rect(screen,cell[0],cell[1])
        screen.unlock()

    def accept(self, id, postions, x_mv, y_mv):    
        for pos in postions:
            x = pos[0]+x_mv
            y = pos[1]+y_mv
            if self.cells.has_key((x,y)):
                cell = self.cells[(x,y)]
                if cell and cell[2] != id and cell[2] != 0:
                    return False
            else:
                return False
        return True
        
    def checkForLines(self):
        nums = {}
        #Test for y coords with all thier x coords filled up
        #If so then set that line of x,y coords to masking color and move the rest of the coords
        #above it down one y coord
        for cell in self.cells:
            y = cell[1]
            if not nums.has_key(y):
                nums[y] = 0                        
            if self.cells[cell][2] > 0:
                nums[y] += 1
        for num in nums:
            if nums[num] >= self.num_cells_wide:
                self.sound.play("../sound/clear.wav")
                self.numLinesCleared += 1
                self.remLine(num)
                self.shiftGridDown(num)
                
    def topY(self):
        top = self.num_cells_tall
        for cell in self.cells:
            y = cell[1]
            if y < top and self.cells[cell][2] > 0:
                top = y
        return top
            
    def remLine(self, y):
        for cell_x in range(self.num_cells_wide):
            # ADDED: color accumulation on line finish
            current_cell_color = self.cells[(cell_x, y)][0]
            if current_cell_color not in self.color_accum.keys():
                self.color_accum[current_cell_color] = 1
            else:
                self.color_accum[current_cell_color] += 1
            self.set(self.color,cell_x,y,0)
            
    def shiftGridDown(self,num):
        n_cells = {}
        for cell in self.cells:
            x     = cell[0]
            y     = cell[1]
            color = self.cells[cell][0]
            id    = self.cells[cell][2]
            if y < num:
                self.set(self.color,x,y,id)
                n_cells[(x,y+1)] = (color,Rect((x*self.cell_width+self.start_x,
                                                y*self.cell_height+self.start_y),
                                                (self.cell_height,self.cell_width)),id)                
        for n_cell in n_cells:
            x     = n_cell[0]
            y     = n_cell[1]
            color = n_cells[n_cell][0]
            id    = n_cells[n_cell][2]            
            self.set(color,x,y,id)
