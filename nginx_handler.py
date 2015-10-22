#!/usr/bin/python
# -*- coding:utf8 -*-
__author__ = 'jjj'

from jinja2 import Environment, PackageLoader
import os
from subprocess import call
import signal
import sys
import time

env = Environment(loader=PackageLoader('fuck', 'templates'))
POLL_TIMEOUT=2
signal.signal(signal.SIGCHLD, signal.SIG_IGN)

class NginxHandler:
    def get_services(self, numbers = []):
        dirs = os.listdir('/var/run/durian')

        if len(numbers) != 0:
            try:
                for i in numbers:
                    dirs.remove(i)
            except ValueError:
                print 'there is no fpm_sock_id in', i
                sys.exit(1)

        return dirs

    def generate_config(self, services):
        template = env.get_template('cfg.tmpl')
        with open("bb.conf", "w") as f:
            f.write(template.render(services=services))

    def reload_nginx(self):
        print "config changed. reload nginx"
        ret = call(["nginx", "-s", "reload"])
        if ret != 0:
            print "reloading nginx returned: ", ret 

    #fpmId should be a list
    def offline_fpm(self, fpmId = []):
        fpmId = map(str, fpmId)

        try:

            #if fpmId != "" and not fpmId.isdigit():
            #        raise ValueError('fpmId must be a number') 

            services = self.get_services(fpmId)

            if not services:
                raise EOFError("there is no service")

            self.generate_config(services)
            self.reload_nginx() 

        except Exception, e:
            print "Error:", e

    def renew_nginx_setting(self):
        self.offline_fpm()

