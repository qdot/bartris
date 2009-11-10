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
import pygame
from pygame.locals import *

class Sound(object):
    def __init__(self):
        self.volume   = 1.0
        self.freq     = 44100
        self.bitsize  = -32
        self.channels = 2
        self.buffer   = 4096

        if pygame.mixer:
            pygame.mixer.init()
            pygame.mixer.music.set_volume(self.volume)

    def play(self,mfile):
        self.mfile = mfile
        self.sound = pygame.mixer.Sound(self.mfile)               
        self.sound.play()