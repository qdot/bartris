#!/usr/bin/env python
"""
    Too Much Tetris is a tetris clone with event hooking for whatever system I want
    Copyright (C) 2009 Kyle Machulis/Nonpolynomial Labs <kyle@nonpolynomial.com

    Too Much Tetris is derived from:
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

import sys, pygame, time, random, os, operator, string
from Tetromino     import *
from Grid          import *
from Sound         import *
from pygame.locals import *
from math          import *
from types         import *

os.environ["DYLD_LIBRARY_PATH"] = "/Users/qdot/git-projects/library/usr_darwin_10.5_x86/lib/"
sys.path.append('/Users/qdot/git-projects/library/usr_darwin_10.5_x86/lib/python2.6/site-packages')
from ambx import *
import osc
import serial


def hexDump(bytes):
    """Useful utility; prints the string in hexadecimal"""
    for i in range(len(bytes)):
        sys.stdout.write("%2x " % (ord(bytes[i])))
        if (i+1) % 8 == 0:
            print repr(bytes[i-7:i+1])

    if(len(bytes) % 8 != 0):
        print string.rjust("", 11), repr(bytes[i-len(bytes)%8:i+1])

class QuitException(Exception):
    def __init__(self, msg = "Quitting"):
        Exception.__init__(self, msg)

class TetrisEventHandler():
    def on_level_up(self, tetris_obj):
        return

    def on_line_created(self, tetris_obj):
        return

COLORS = {
    "black"               : (0,0,0),
    "white"               : (255, 255, 255),
    "blue"                : (0,0,255),
    "red"                 : (255,0,0),
    "grey"                : (171,171,171),
    "darkGrey"            : (85,85,85),
    "brown"               : (0x8e, 0x48, 0x1d)
    }

DRINK_PORTS = {
    "water" : 0,
    "coke" : 1,
    "rum" : 2
}

DRINK_COLORS = {
    COLORS["darkGrey"] : "rum",
    COLORS["brown"] : "coke",
    COLORS["blue"] : "water"
}

class Tetris():

    NORMAL_MODE = 0
    BOOZE_MODE = 1
    DESIGNATED_DRIVER_MODE = 2
    SINGLE_DRINK_MODE = 3

    def __init__(self):
        self._event_handlers = []
        self._setup_states()
        self._state["game_over"] = True
        self._setup_display()

    def _setup_states(self, mode = 0):
        self._params = {
            "fullscreen"             : False,
            "fullscreen_width"       : 1024,
            "fullscreen_height"      : 768,
            "num_cells_wide"         : 10,
            "num_cells_high"         : 20,
            "cell_width"             : 25,
            "cell_height"            : 25,
            "drink_pouring_time"     : 5.0,
            "starting_cell_x"        : 4,
            "starting_cell_y"        : 1,
            "grid_top_x"             : 0,
            "grid_top_y"             : 0,
            "modes"                  : ["(N)ormal Mode", "(B)ooze Mode", "(S)ingle Drink Mode", "(D)esignated Driver Mode", "(Q)uit"]
            }

        self._level_params = {
            "moving_rate"            : [0.00005,.00004,0.00003,0.00002,0.00001],
            "rotating_rate"          : [0.00009,0.00008,0.00007,0.00006,0.00005],
            "falling_rate"           : [0.00050,0.00035,0.00020,0.00010,0.00005]
            }

        self._state = {
            "last_falling_time"      : 0,
            "falling_rate"           : self._level_params["falling_rate"][0],
            "last_moving_time"       : 0,
            "last_rotating_time"     : 0,
            "level_up_line_count"    : 2,
            "last_num_lines_cleared" : 0,
            "top_y"                  : 0,
            "times_found"            : 0,
            "current_level"          : 1,
            "game_over"              : False,
            "all_finished"           : False,
            "current_y"              : 0,
            "holding_down"           : False
            }


        if mode in [self.NORMAL_MODE, self.SINGLE_DRINK_MODE]:
            self._color_dict     = {1: COLORS["blue"], 6 : COLORS["brown"], 10: COLORS["darkGrey"]}
        elif mode == self.BOOZE_MODE:
            self._color_dict     = {3 : COLORS["brown"], 10: COLORS["darkGrey"]}
        elif mode == self.DESIGNATED_DRIVER_MODE:
            self._color_dict     = {10: COLORS["blue"]}

        if mode == self.SINGLE_DRINK_MODE:
            self._level_params = {
                "moving_rate"            : [0.00005],
                "rotating_rate"          : [0.00009],
                "falling_rate"           : [0.00040]
                }

        self._color_range    = 10

        self._textBuff       = 2
        self._grid           = Grid( 1, 1, self._params["cell_width"], self._params["cell_height"], self._params["num_cells_wide"], self._params["num_cells_high"], COLORS["black"], self._params["fullscreen"], self._params["fullscreen_width"], self._params["fullscreen_height"])
        if self._params["fullscreen"]:
            self._params["grid_top_x"] = (self._params["fullscreen_width"] / 2) - (self._grid.width / 2)
            self._params["grid_top_y"] = (self._params["fullscreen_height"] / 2) - (self._grid.height / 2)

        self._tetrominoList  = ['T','I','O','S','Z','L','J']
        self._sound          = Sound()

        self._new_tetromino()

    def _setup_display(self):
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        pygame.init()
        if self._params["fullscreen"]:
            self._screen = pygame.display.set_mode((1024, 768), pygame.FULLSCREEN, 24)
        else:
            self._screen = pygame.display.set_mode((self._grid.width+self._textBuff,self._grid.height+self._textBuff),0,32)
        if pygame.font:
            self._font = pygame.font.Font(None, 18)

    def init_game(self):
        pygame.display.set_caption("Python Tetris")

    def run_game(self):
        time.sleep(0.01)
        if self._state["game_over"]:
            self._menu_state()
        else:
            self._game_loop()
        self._render()
        return

    def _menu_state(self):
        current_key = ''
        for event in pygame.event.get():
            if event.type == QUIT:
                raise QuitException()
            if event.type == pygame.KEYDOWN:
                current_key = event.key
        if current_key == K_q:
            raise QuitException()
        elif current_key == K_n:
            self._setup_states(self.NORMAL_MODE)
        elif current_key == K_b:
            self._setup_states(self.BOOZE_MODE)
        elif current_key == K_d:
            self._setup_states(self.DESIGNATED_DRIVER_MODE)
        elif current_key == K_s:
            self._setup_states(self.SINGLE_DRINK_MODE)

    def _game_loop(self):

        # Grab vars
        if self._tetromino.active:
            self._move_tetromino()
        else: #New Tetromino
            self._new_tetromino()
        #Levels and Speedup
        if self._grid.num_lines_cleared >= (self._state["level_up_line_count"] * self._state["current_level"]) and self._state["last_num_lines_cleared"] != self._grid.num_lines_cleared:
            self._level_up()

    def _move_tetromino(self):

        current_key = ''
        up_key = ''
        for event in pygame.event.get():
            legal_moves   = {
                "down"  : self._tetromino.max_y < self._grid.height,
                "left"  : self._tetromino.min_x > 0 and self._grid.accept(self._tetromino.id,self._tetromino.positions[self._tetromino.currentPosition],-1,0),
                "right" : self._tetromino.max_x < self._grid.width and self._grid.accept(self._tetromino.id,self._tetromino.positions[self._tetromino.currentPosition],1,0),
                }

            if event.type == QUIT:
                break
            if event.type == pygame.KEYDOWN:
                current_key = event.key
            elif event.type == pygame.KEYUP:
                up_key = event.key

            if current_key == K_RIGHT and legal_moves["right"]:
                self._tetromino.move(self._grid,1,0)
            if current_key == K_LEFT and legal_moves["left"]:
                self._tetromino.move(self._grid,-1,0)
            if current_key == K_DOWN:
                self._state["holding_down"] = True
            elif up_key == K_DOWN:
                self._state["holding_down"] = False
            #TODO: Fix rotation states
            if current_key == K_UP and False not in legal_moves.values():
                self._tetromino.rotate(self._grid)
            #ADDED: quit current_key
            if current_key == K_q:
                raise QuitException()

        legal_moves   = {
            "down"  : self._tetromino.max_y < self._grid.height,
            "left"  : self._tetromino.min_x > 0 and self._grid.accept(self._tetromino.id,self._tetromino.positions[self._tetromino.currentPosition],-1,0),
            "right" : self._tetromino.max_x < self._grid.width and self._grid.accept(self._tetromino.id,self._tetromino.positions[self._tetromino.currentPosition],1,0),
            }

        current_time  = time.time()/1000.0
        falling_time  = current_time - self._state["last_falling_time"]

        #Downward fall
        if self._state["holding_down"] is True and legal_moves["down"]:
            self._tetromino.move(self._grid,0,1)
            self._state["current_y"] += 1
        elif falling_time >= self._state["falling_rate"] and legal_moves["down"]:
            self._state["last_falling_time"] = current_time
            self._tetromino.move(self._grid,0,1)
            self._state["current_y"] += 1
        elif not legal_moves["down"] and falling_time >= self._state["falling_rate"]:
            self._tetromino.cluck.play()
            self._tetromino.active = False

    def _new_tetromino(self):
        #ADDED: Set tetromino color to one of our three allowed colors
        color_index = random.randint(0,self._color_range)
        color = ()
        for color_probability in sorted(self._color_dict.keys()):
            if color_index <= color_probability:
                color = self._color_dict[color_probability]
                break

        rand          = random.randint(0,len(self._tetrominoList)-1)
        self._tetromino = Tetromino(self._params["starting_cell_x"], self._params["starting_cell_y"], COLORS["black"],color,self._tetrominoList[rand])
        self._state["holding_down"] = False
        if self._grid.checkForLines():
            for e in self._event_handlers:
                e.on_line_created(self)

        #Test for GAME OVER
        top_y = self._grid.topY()
        if top_y <= 2:
            self._state["times_found"] += 1
        if self._state["times_found"] > 3:
            self._state["game_over"] = True

    def _level_up(self):
        self._state["last_num_lines_cleared"] = self._grid.num_lines_cleared
        self._state["current_level"] += 1
        if self._state["current_level"] < len(self._level_params["falling_rate"]):
            self._state["falling_rate"] = self._level_params["falling_rate"][self._state["current_level"]]
        else:
            self._state["all_finished"] = True
            self._state["game_over"] = True
        self._sound.play("../sound/levelup.wav")
        for e in self._event_handlers:
            e.on_level_up(self)

    def _render(self):
        #render Background
        pygame.draw.rect(self._screen,(255,255,255),Rect(self._params["grid_top_x"], self._params["grid_top_y"],self._grid.width+2,self._grid.height+2))
        #Render Grid
        self._grid.render(self._screen)
        self._render_status()
        pygame.display.update()

    def _render_status(self):
        if not self._state["game_over"]:
            lineText       = "Lines: " + str(self._grid.num_lines_cleared) + "  Level: " + str(self._state["current_level"])
            lines_text     = self._font.render(lineText, 1, COLORS["white"])
            lines_text_pos = Rect((self._params["grid_top_x"]+1, self._params["grid_top_y"]+1),(self._params["grid_top_x"] + 300, self._params["grid_top_y"] + 20))
            self._screen.blit(lines_text, lines_text_pos)
        else:
            game_over_text     = self._font.render("GAME OVER... LEVEL: "+str( self._state["current_level"])+" LINES: " + str(self._grid.num_lines_cleared),1, COLORS["red"])
            if self._state["all_finished"]:
                game_over_text     = self._font.render("ALL LEVELS FINISHED! LEVEL: "+str( self._state["current_level"])+" LINES: " + str(self._grid.num_lines_cleared),1, COLORS["red"])
            game_over_text_pos = Rect((self._params["grid_top_x"]+1, self._params["grid_top_y"]+1),(self._params["grid_top_x"] + 300, self._params["grid_top_y"] + 20))
            self._screen.blit(game_over_text,game_over_text_pos)
            for i in range(0, len(self._params["modes"])):
                pLineText       = self._params["modes"][i]
                p_lines_text     = self._font.render(pLineText, 1, COLORS["white"])
                p_lines_text_pos = Rect((1+self._params["grid_top_x"],100+(i*25)+self._params["grid_top_y"]),(300,250))
                self._screen.blit(p_lines_text, p_lines_text_pos)


    def add_event_handler(self, eh):
        self._event_handlers.append(eh)

class SerialServo():
    def __init__(self):
        self.serial = serial.Serial(port="/dev/tty.usbserial-A6004oBL", baudrate=38400)

    def checksum(self, msg):
        return reduce(operator.add, map(ord, msg)) % 256

    def sendCommand(self, speed_list):
        command = ''.join(['a'] + map(chr, speed_list))
        command += chr(self.checksum(command))
        self.serial.write(command)

    def isOpen(self):
        return self.serial.isOpen()

class Bartris(TetrisEventHandler):
    def __init__(self):
        self.SERVO_DOWN_POS  = 70
        self.SERVO_UP_POS    = 160
        self.SERVO_DOWN_LIST = [self.SERVO_DOWN_POS, self.SERVO_DOWN_POS, self.SERVO_DOWN_POS]
        self.COLOR_PORT      = {COLORS["blue"]: 1, COLORS["brown"]: 0, COLORS["white"]: 2}
        self._serial = None
        try:
            self._serial = SerialServo()
        except Exception, e:
            print "SERIAL PORT NOT FOUND, NOT USING BARTRIS"
            pass

    def _render_list(self, tetris_obj, color_list):
        self._ingredient_font = pygame.font.Font(None, 30)
        self._percentage_font = pygame.font.Font(None, 60)

        lineText       = "/".join([DRINK_COLORS[x] for x in color_list.keys()])
        lines_text     = self._ingredient_font.render(lineText, 1, COLORS["white"])
        lines_text_pos = Rect((1+tetris_obj._params["grid_top_x"],50+tetris_obj._params["grid_top_y"]),(300,150))
        pLineText       = "/".join(map(str, [int(x*100) for x in color_list.values()]))
        p_lines_text     = self._percentage_font.render(pLineText, 1, COLORS["white"])
        p_lines_text_pos = Rect((1+tetris_obj._params["grid_top_x"],100+tetris_obj._params["grid_top_y"]),(300,250))
        tetris_obj._screen.blit(lines_text, lines_text_pos)
        tetris_obj._screen.blit(p_lines_text, p_lines_text_pos)
        pygame.display.update()

    def on_level_up(self, tetris_obj):
        grid = tetris_obj._grid
        #ADDED: Color accumulation output and reset on level finish
        total_cells = sum(grid.color_accum.values())
        color_timing = dict([(c, (float(x) / float(total_cells))) for c, x in grid.color_accum.items()])
        self._render_list(tetris_obj, color_timing)
        color_timing = dict([(c, (float(x) / float(total_cells)) * tetris_obj._params["drink_pouring_time"]) for c, x in grid.color_accum.items()])
        for color, hold_time in color_timing.items():
            osc.sendMsg("/tetris/level", [ DRINK_PORTS[DRINK_COLORS[color]], hold_time], "localhost", 9001)
            time.sleep(hold_time + 1)
            time.sleep(2)
        grid.color_accum = {}

class amBXtris(TetrisEventHandler):
    def __init__(self):
        return

    def on_line_created(self, tetris_obj):
        grid = tetris_obj._grid
        total_cells = sum(grid.color_accum.values())
        rgb_list = [[x * (float(value) / float(total_cells)) for x in key] for key, value in grid.color_accum.items()]
        color = [0,0,0]
        for c in rgb_list:
            color = map(operator.add, color, c)
        color = map(int, color)
        osc.sendMsg("/tetris/line", color, "localhost", 9001)

def main(argv=None):
    osc.init()

    b = Bartris()
    t = Tetris()
    a = amBXtris()
    t.add_event_handler(a)
    t.add_event_handler(b)
    t.init_game()
    try:
        while(1):
            t.run_game()
    except QuitException, e:
        return 0

if __name__ == "__main__":
    sys.exit(main())
