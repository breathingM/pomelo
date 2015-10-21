#!/usr/bin/python
# -*- coding:utf8 -*-
__author__ = 'jjj'
#將某一個FPM container 下線

from jinja2 import Environment, PackageLoader
import os
from subprocess import call
import signal
import sys
import time

env = Environment(loader=PackageLoader('fuck', 'templates'))
POLL_TIMEOUT=2
signal.signal(signal.SIGCHLD, signal.SIG_IGN)

def get_services(number):
    dirs = os.listdir('/var/run/durian')
    try:
        dirs.remove(number)
    except ValueError:
        print 'there is no fpm_sock_id in', number
        exit(1)
    return dirs

def generate_config(services):
    template = env.get_template('cfg.tmpl')
    with open("bb.conf", "w") as f:
        print 1
        f.write(template.render(services=services))

def print_usage():
    print "Usage: offline_nginx_config.py fpm_container_id(a number)"
    exit(1)

if __name__ == "__main__":
    current_services = []
    while True:
        try:

            if len(sys.argv) != 2:
                print_usage()

            if not sys.argv[1].isdigit():
                print_usage()

            services = get_services(sys.argv[1])

            if not services or services == current_services:
                print "config has no changes"
                time.sleep(POLL_TIMEOUT)
                continue

            print "config changed. reload nginx"
            generate_config(services)
            ret = call(["nginx", "-s", "reload"])
            if ret != 0:
                print "reloading nginx returned: ", ret
                time.sleep(POLL_TIMEOUT)
                continue
            current_services = services

        except Exception, e:
            print "Error:", e

        time.sleep(POLL_TIMEOUT)
