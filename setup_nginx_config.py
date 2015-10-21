#!/usr/bin/python
# -*- coding:utf8 -*-
__author__ = 'jjj'
#初始化nginx設定檔

from jinja2 import Environment, PackageLoader
import os
from subprocess import call
import signal
import sys
import time

env = Environment(loader=PackageLoader('fuck', 'templates'))
POLL_TIMEOUT=2
signal.signal(signal.SIGCHLD, signal.SIG_IGN)

def get_services():
    return os.listdir('/var/run/durian')

def generate_config(services):
    template = env.get_template('cfg.tmpl')
    with open("bb.conf", "w") as f:
        f.write(template.render(services=services))

if __name__ == "__main__":
    current_services = []
    while True:
        try:
            services = get_services()

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
