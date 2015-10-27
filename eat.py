#!/usr/bin/env python

import sys
import getopt
import pomelo

def usage():
    print "Usage:%s [-h] [--help|--run|--renew|--off|--roll|--del] args..." % (sys.argv[0])
    sys.exit(0)

if "__main__" == __name__:
    obj = pomelo.Pomelo()

    try:
        opts, args = getopt.getopt(sys.argv[1:], "h", ["help", "run", "renew", "off=", "roll", "del="]);
    except getopt.GetoptError as err:
        print str(err)
        usage()

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("--run"):
            obj.create_container()
        elif o in ("--renew"):
            obj.renew_nginx_setting()
        elif o in ("--off"):
            fpmIds = [a]
            for i in args:
                fpmIds.append(i)
            obj.offline_fpm(fpmIds)
        elif o in ("--roll"):
            obj.rolling_update()
        elif o in ("--del"):
            fpmIds = [a]
            for i in args:
                fpmIds.append(i)
            obj.delete_container(fpmIds)

        sys.exit(0)

