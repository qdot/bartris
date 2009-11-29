import sys
sys.path.append('/Users/qdot/git-projects/library/usr_darwin_10.5_x86/lib/python2.6/site-packages')
import operator
import time
import osc
import trancevibe
import threading
import serial
from ambx import ambx

################################################################################

class ArduinoDrinkControl():
    WATER = 0
    COKE = 1
    RUM = 2
    SERVO_DOWN_POS  = 70
    SERVO_UP_POS    = 160

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
    def __init__(self, t):
        BaseThread.__init__(self)
        self._run_time = t

    def run(self):
        tv = trancevibe.TranceVibrator()
        tv.open(0)
        tv.set_speed(255)
        try:
            time.sleep((255 - self._run_time) * .005)
        except Exception, e:
            print e
            print "EXCEPTION?"
        tv.set_speed(0)
        tv.close()

################################################################################

class ambxThread(BaseThread):
    lights = [ambx.LEFT_SP_LIGHT, ambx.LEFT_WW_LIGHT, ambx.CENTER_WW_LIGHT, ambx.RIGHT_WW_LIGHT, ambx.RIGHT_SP_LIGHT]
    colors = [(0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0)]
    fans = [ambx.RIGHT_FAN, ambx.LEFT_FAN]
    fan_speed = 0
    _need_light_update = False
    _need_fan_update = False

    def __init__(self):
        BaseThread.__init__(self)
        self._ambx = ambx()
        if not self._ambx.open():
            print "No ambx found, not using ambx system"
            self._ambx = None

    def set_all_colors(self, color):
        for i in range(0, 5):
            self.colors[i] = color
        self._need_light_update = True

    def set_color(self, index, color):
        self.colors[i] = color
        self._need_light_update = True

    def set_fan_speed(self, speed):
        self.fan_speed = speed
        self._need_fan_update = True

    def run(self):
        if self._ambx is None:
            print "No ambx found, not running ambx thread"
            return
        try:
            print "Starting ambx thread"
            self.should_run = True
            while self.should_run:
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
            if g_drinkControlThread.get_time(ArduinoDrinkControl.COKE) > 0:
                g_drinkControlThread.add_to_time(ArduinoDrinkControl.COKE, .1)
            else:
                g_drinkControlThread.add_to_time(ArduinoDrinkControl.COKE, .2)
        except Exception, e:
            print e

    def on_flag(self, *msg):
        try:
            v = TranceVibratorThread(msg[0][2])
            v.start()
        except Exception, e:
            print e

    def bind_osc(self, osc):
        print "Binding Mario functions"
        osc.bind(self.on_coin, "/mario/coin")
        osc.bind(self.on_flag, "/mario/flag")
        osc.bind(self.on_speed, "/mario/speed")
        osc.bind(self.on_sky, "/mario/sky")

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
        return

################################################################################

class TetrisHandler():
    def __init__(self):
        return

    def bind_osc(self, osc):
        print "Binding Tetris Functions"
        osc.bind(self.on_line, "/tetris/line")
        osc.bind(self.on_level, "/tetris/level")

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
