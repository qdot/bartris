import sys
sys.path.append('/Users/qdot/git-projects/library/usr_darwin_10.5_x86/lib/python2.6/site-packages')
import os
os.environ["DYLD_LIBRARY_PATH"] = "/Users/qdot/git-projects/library/usr_darwin_10.5_x86/lib/"
import operator
import time
import osc
import trancevibe
import threading
import serial
import traceback
from ambx import ambx

################################################################################

class ArduinoDrinkControl():
    WATER = 2
    COKE = 0
    RUM = 1

    SERVO_DOWN_POS  = 150
    SERVO_UP_POS    = 180

    def __init__(self):
        self.SERVO_DOWN_LIST = [self.SERVO_DOWN_POS, self.SERVO_DOWN_POS,
                                self.SERVO_DOWN_POS]
        self.current_servo_pos = self.SERVO_DOWN_LIST

        self.serial = serial.Serial(port="/dev/tty.usbserial-A6004oBL",
                                    baudrate=38400)

    def checksum(self, msg):
        return reduce(operator.add, map(ord, msg)) % 256

    def sendCommand(self):
        command = ''.join(['a'] + map(chr, self.current_servo_pos))
        command += chr(self.checksum(command))
        self.serial.write(command)

    def isOpen(self):
        return self.serial.isOpen()

################################################################################

class BaseThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.should_run = False

################################################################################

class ArduinoDrinkControlThread(BaseThread):

    current_time = [0.0, 0.0, 0.0]
    start_time = [0,0,0]

    l = threading.Lock()

    def __init__(self):
        BaseThread.__init__(self)
        self._drink_control = None
        try:
            self._drink_control = ArduinoDrinkControl()
        except Exception, e:
            print "SERIAL PORT NOT FOUND, NOT USING ARDUINO"
            pass

    def add_to_time(self, index, time):
        self.l.acquire()
        self.current_time[index] += time
        self.l.release()

    def get_time(self, index):
        return self.current_time[index]

    def run(self):
        if self._drink_control is None:
            return
        self.should_run = True
        while self.should_run:
            should_send = False
            for i in range(0, 3):
                self.l.acquire()
                if self.current_time[i] > 0:
                    if (time.time() - self.start_time[i]) > self.current_time[i] and self._drink_control.current_servo_pos[i] == ArduinoDrinkControl.SERVO_UP_POS:
                        self._drink_control.current_servo_pos[i] = ArduinoDrinkControl.SERVO_DOWN_POS
                        self.current_time[i] = 0.0
                        should_send = True
                    elif self._drink_control.current_servo_pos[i] == ArduinoDrinkControl.SERVO_DOWN_POS and self.current_time[i] > 0:
                        self._drink_control.current_servo_pos[i] = ArduinoDrinkControl.SERVO_UP_POS
                        self.start_time[i] = time.time()
                        should_send = True
                self.l.release()
            if should_send:
                self._drink_control.sendCommand()
            else:
                time.sleep(0.005)

g_drinkControlThread = ArduinoDrinkControlThread()

################################################################################

class TranceVibratorThread(BaseThread):
    current_time = 0
    run_time = -1
    t = threading.Lock()    

    def __init__(self):
        BaseThread.__init__(self)
        try:
            self.tv = trancevibe.TranceVibrator()
            self.tv.open(0)
        except Exception, e:
            print "TRANCEVIBE EXCEPTION"
            print e
            self.tv = None

    def set_time(self, s = 0):
        try:
            self.t.acquire()
            self.run_time = s
            self.current_time = time.time()
            self.tv.set_speed(255)
        except Exception, e:
            print traceback.print_exc()
            print e
            print "EXCEPTION?"
        finally:
            self.t.release()

    def run(self):
        if self.tv is None:
            return
        self.should_run = True
        try:
            while self.should_run:
                if self.run_time > 0:
                    if time.time() - self.current_time > self.run_time:
                        self.t.acquire()
                        self.tv.set_speed(0)
                        self.run_time = 0
                        self.t.release()
                time.sleep(.005)
            self.tv.set_speed(0)
            self.tv.close()
        except Exception, e:
            print traceback.print_exc()
            print e
            print "EXCEPTION?"
        finally:
            self.t.release()
g_tranceVibratorThread = TranceVibratorThread()

################################################################################

class ambxThread(BaseThread):
    lights = [ambx.LEFT_SP_LIGHT, ambx.LEFT_WW_LIGHT, ambx.CENTER_WW_LIGHT, ambx.RIGHT_WW_LIGHT, ambx.RIGHT_SP_LIGHT]
    colors = [(0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0)]
    fans = [ambx.RIGHT_FAN, ambx.LEFT_FAN]
    fan_speed = 0
    _need_light_update = False
    _need_fan_update = False
    color_time = 0
    last_time = 0
    old_colors = []

    def __init__(self):
        BaseThread.__init__(self)
        self._ambx = ambx()
        if not self._ambx.open():
            print "No ambx found, not using ambx system"
            self._ambx = None

    def clear_timed_color(self):
        if self.color_time > 0:
            print "clearing timed color"
            self.colors = self.old_colors
            self._need_light_update = True
            self.color_time = 0

    def set_all_colors(self, color):
        self.clear_timed_color()
        for i in range(0, 5):
            self.colors[i] = color
        print self.colors
        self._need_light_update = True

    def set_color(self, index, color):
        self.clear_timed_color()
        self.color_time = 0
        self.colors[i] = color
        self._need_light_update = True

    def set_fan_speed(self, speed):
        self.fan_speed = speed
        self._need_fan_update = True

    def set_timed_color(self, color, t):
        self.clear_timed_color()
        self.old_colors = list(self.colors)
        self.set_all_colors(color)
        self.color_time = t
        self.last_time = time.time()

    def run(self):
        if self._ambx is None:
            print "No ambx found, not running ambx thread"
            return
        try:
            print "Starting ambx thread"
            self.should_run = True
            while self.should_run:
                if self.color_time > 0 and (time.time() - self.last_time) > self.color_time:
                    self.clear_timed_color()
                if self._need_light_update is True:
                    for i in range(0, 5):
                        self._ambx.setLightColor(self.lights[i], self.colors[i])
                    self._need_light_update = False
                if self._need_fan_update is True:
                    for i in range(0, 2):
                        self._ambx.setFanSpeed(self.fans[i], self.fan_speed)
                    self._need_fan_update = False
                time.sleep(.005)
        except Exception, e:
            print e

g_ambxThread = ambxThread()

################################################################################

class OSCServer():
    _handlers = []
    def __init__(self):
        osc.init()
        osc.listen('localhost', 9001)
        osc.listen('10.211.55.2', 9001)

        self._threads = []
        self._threads.append(g_drinkControlThread)
        self._threads.append(g_ambxThread)
        self._threads.append(g_tranceVibratorThread)
        [thread.start() for thread in self._threads]

    def add_handler(self, h):
        self._handlers.append(h)
        h.bind_osc(osc)

    def close(self):
        osc.dontListen()
        for thread in self._threads:
            thread.should_run = False

################################################################################

class OSCBinder():
    def bind_osc(self, osc):
        return

################################################################################

class MarioHandler(OSCBinder):
    def __init__(self):
        return

    def on_coin(self, *msg):
        try:
            print "Coin!"
            if g_drinkControlThread.get_time(ArduinoDrinkControl.COKE) > 0:
                g_drinkControlThread.add_to_time(ArduinoDrinkControl.COKE, .2)
            else:
                g_drinkControlThread.add_to_time(ArduinoDrinkControl.COKE, .4)
            g_ambxThread.set_timed_color((0xf3, 0xff, 0x39), .5)
        except Exception, e:
            print e

    def on_die(self, *msg):
        try:
            g_drinkControlThread.add_to_time(ArduinoDrinkControl.WATER, 2.0)
        except Exception, e:
            print e

    def on_enemy(self, *msg):
        try:
            print "Enemy!"
            if g_drinkControlThread.get_time(ArduinoDrinkControl.RUM) > 0:
                g_drinkControlThread.add_to_time(ArduinoDrinkControl.RUM, .4)
            else:
                g_drinkControlThread.add_to_time(ArduinoDrinkControl.RUM, .2)
            g_ambxThread.set_timed_color((255, 0, 0), .5)
        except Exception, e:
            print e

    def on_flag(self, *msg):
        try:
            g_tranceVibratorThread.set_time((255 - msg[0][2]) * .005)
            g_drinkControlThread.add_to_time(ArduinoDrinkControl.RUM, .75 * (255.0-msg[0][2]) / 255.0)
        except Exception, e:
            print e

    def bind_osc(self, osc):
        print "Binding Mario functions"
        osc.bind(self.on_coin, "/mario/coin")
        osc.bind(self.on_flag, "/mario/flag")
        osc.bind(self.on_speed, "/mario/speed")
        osc.bind(self.on_sky, "/mario/sky")
        osc.bind(self.on_die, "/mario/die")
        osc.bind(self.on_enemy, "/mario/enemy")

    def on_speed(self, *msg):
        try:
            s = 0
            # Going backwards
            if msg[0][2] > 200:
                s = (int)(((256 - msg[0][2]) / 40.0) * 255)
            # Going forwards
            else:
                s = (int)(((msg[0][2]) / 40.0) * 255)
            g_ambxThread.set_fan_speed(s)
            return
        except Exception, e:
            print msg
            print e

    def on_sky(self, *msg):
        sky_color = [(0, 0, 20), (0, 0, 180), (0, 0, 180), (255,0,0), (0,0,0)]
        color = sky_color[msg[0][2]]
        g_ambxThread.set_all_colors(color)
        return

################################################################################

class TetrisHandler():
    def __init__(self):
        return

    def bind_osc(self, osc):
        print "Binding Tetris Functions"
        osc.bind(self.on_line, "/tetris/line")
        osc.bind(self.on_level, "/tetris/level")
        osc.bind(self.on_piece_down, "/tetris/piece_down")

    def on_piece_down(self, *msg):
        try:
            g_tranceVibratorThread.set_time(.2)
        except Exception, e:
            print traceback.print_exc()
            print "EX"
            print e

    def on_line(self, *msg):
        color = msg[0][2:5]
        g_ambxThread.set_all_colors(color)
        return

    def on_level(self, *msg):
        #print msg
        g_drinkControlThread.add_to_time(msg[0][2], msg[0][3])
        return

################################################################################

def main():
    s = OSCServer()
    s.add_handler(MarioHandler())
    s.add_handler(TetrisHandler())

    try:
        while 1:
            time.sleep(0.01)
    except KeyboardInterrupt, e:
        pass
    except Exception, ex:
        print "EXCEPTION!"
        print ex
    finally:
        print "CLOSING CONNECTION"
        s.close()

if __name__ == '__main__':
    sys.exit(main())
