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
        for i in range(0, 3):
            osc.sendMsg("/tetris/level", [i, .5], "localhost", 9001)
            time.sleep(1)
        pass
    except Exception, ex:
        print "EXCEPTION!"
        print ex

if __name__ == '__main__':
    sys.exit(main())

