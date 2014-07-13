import sys
import os
import urllib2
import time
import serial
def main():
    print "Polling Second Life for drink status"
    try:
        s = serial.Serial("/dev/tty.usbserial-A9007MET", 9600)
        while(1):
            try:
                s.read()
                f = urllib2.urlopen(url = 'http://sim9736.agni.lindenlab.com:12046/cap/e11488fc-9cf5-5fa7-f0d3-9b60174a34501', data = "0,0,10", timeout = 5)
            except Exception:
                print "TIMEOUT"
                continue
            f.readline()
            #time.sleep(1)
            sys.exit(0)
    except KeyboardInterrupt:
        print "Exiting polling loop"
        pass

if __name__ == '__main__':
    sys.exit(main())
