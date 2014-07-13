import sys
sys.path.append('/Users/qdot/git-projects/library/usr_darwin_10.5_x86/lib/python2.6/site-packages')
import os
os.environ["DYLD_LIBRARY_PATH"] = "/Users/qdot/git-projects/library/usr_darwin_10.5_x86/lib/"
import operator
import time
import osc
import threading
import random

def main():
    osc.init()
    try:
        random.seed()
        while 1:
            a = ((random.randint(0,100) % 100) / 100.0, (random.randint(0,100) % 100) / 100.0, (random.randint(0,100) % 100) / 100.0)
            print a
            b = [int(x * 255) for x in a]
            print b
            c = [random.randint(0, 40)]
            print c
            for i in range(0, 3):
                osc.sendMsg("/tetris/level", [i , a[i]], "localhost", 9001)
            osc.sendMsg("/tetris/line", b, "localhost", 9001)
            osc.sendMsg("/mario/speed", c, "localhost", 9001)
            time.sleep(1.5)
    except KeyboardInterrupt, e:
        osc.sendMsg("/tetris/line", [0,0,0], "localhost", 9001)
        osc.sendMsg("/mario/speed", [0], "localhost", 9001)

        pass
    except Exception, ex:
        print "EXCEPTION!"
        print ex

if __name__ == '__main__':
    sys.exit(main())

