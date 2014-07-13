import sys
import os
import urllib2
import time
def main():
    print "Polling Second Life for drink status"
    last_coke_count = 0
    last_rum_count = 0
    try:
        while(1):
            coke_count = 0
            rum_count = 0
            try:
                f = urllib2.urlopen(url = 'http://sim9736.agni.lindenlab.com:12046/cap/444785ea-8142-546f-cbaf-9a505abbd89b', timeout = 5)
            except Exception:
                print "TIMEOUT"
                continue
            index = f.readline()
            (coke_count, rum_count) = [int(x) for x in index.strip().split(" ")]
            print "%d %d\n" % (coke_count, rum_count)
            if coke_count != last_coke_count:
                if last_coke_count > 0:
                    for i in range(0, coke_count - last_coke_count):
                        time.sleep(.010)
                last_coke_count = coke_count
            if rum_count != last_rum_count:
                if last_rum_count > 0:
                    for i in range(0, rum_count - last_rum_count):
                        time.sleep(.010)
                last_rum_count = rum_count
            time.sleep(1)
    except KeyboardInterrupt:
        print "Exiting polling loop"
        pass

if __name__ == '__main__':
    sys.exit(main())
