#!/usr/bin/python
# -*- coding:utf8 -*-
__author__ = 'jjj'

from jinja2 import Environment, PackageLoader
import os
import subprocess
from subprocess import call
import signal
import sys
import time

env = Environment(loader=PackageLoader('fuck', 'templates'))
POLL_TIMEOUT=2
MAX_CONTAINER_NUM = 10
signal.signal(signal.SIGCHLD, signal.SIG_IGN)

class Pomelo:
    '''
    return the current service container id
    except the numbers you give
    '''
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

    # generate nginx setting by template
    def generate_config(self, services):
        template = env.get_template('cfg.tmpl')
        with open("/etc/nginx/conf.d/fpm.conf", "w") as f:
            f.write(template.render(services=services))

    # reload nginx setting
    def reload_nginx(self):
        print "config changed. reload nginx"
        reloadNginx = "docker exec nginx nginx -s reload"
        proc = subprocess.Popen([reloadNginx], stdout=subprocess.PIPE, shell=True)

    # let some fpm containers offline, fpmId should be a list
    def offline_fpm(self, fpmId = []):
        fpmId = map(str, fpmId)

        try:

            services = self.get_services(fpmId)

            if not services:
                raise EOFError("there is no service")

            self.generate_config(services)
            self.reload_nginx()

        except Exception, e:
            print "Error:", e
            sys.exit(1)

    # update the setting of nginx
    def renew_nginx_setting(self):
        self.offline_fpm()

    # search in /var/run/durian and trying to
    # find an available space to run a new container
    def find_free_space(self):
        dirs = os.listdir('/var/run/durian')
        for i in range(0, MAX_CONTAINER_NUM):
            if str(i) not in dirs:
                return str(i)
            else:
                continue

        print "There is no Space for the new container"
        exit(1)

    
    # run a new fpm container
    def create_container(self):
        a = self.find_free_space()

        dockerRun = "docker run -d --privileged -v /etc/localtime:/etc/localtime \
                    -v /var/run/durian/{0}:/var/run/durian -v /var/log/php-fpm:/var/log/php-fpm \
                    -v /home/durian:/home/durian -v /dev/shm:/dev/shm --name fpm{0} fpm_2".format(a)
        print dockerRun
        proc = subprocess.Popen([dockerRun], stdout=subprocess.PIPE, shell=True)

    '''
    restart each fpm container one by one
    before that it will offline it from nginx
    '''
    def rolling_update(self):
        dirs = os.listdir('/var/run/durian')

        for i in dirs:
            self.offline_fpm(i)
            time.sleep(POLL_TIMEOUT)
            dockerRestart = "docker restart fpm{0}".format(i)
            print dockerRestart
            proc = subprocess.Popen([dockerRestart], stdout=subprocess.PIPE, shell=True)

        self.renew_nginx_setting()

    '''
    put the container offline
    and remove the container, delete the sock in /var/run/durian
    '''
    def delete_container(self, fpmId):
        fpmId = map(str, fpmId)
        self.offline_fpm(fpmId)

        for i in fpmId:
            dockerStr = "docker rm -f fpm%s" % (i)
            print dockerStr
            proc = subprocess.Popen([dockerStr], stdout=subprocess.PIPE, shell=True)
            sockDelete = "rm -rf /var/run/durian/%s" % (i)
            proc = subprocess.Popen([sockDelete], stdout=subprocess.PIPE, shell=True)

