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
import socket
import re

env = Environment(loader=PackageLoader('fuck', 'templates'))
POLL_TIMEOUT=2
MAX_CONTAINER_NUM = 20
signal.signal(signal.SIGCHLD, signal.SIG_IGN)

class Pomelo:
    '''
    return the current service container id
    except the numbers you give
    '''
    def get_services(self, numbers = []):
        dirs = os.listdir('/var/run/durian')
        oldSock = []

        # if there has any fpm_old container
        # dont return the sock of them
        proc = subprocess.Popen(["docker ps | grep -o -E 'old\w+'"], stdout=subprocess.PIPE, shell=True)
        oldContainersName = proc.stdout.readlines()

        if oldContainersName:
            pattern = re.compile(r'\d')
            for i in oldContainersName:
                item = re.search(pattern, i)
                oldSock.append(item.group())

            for sock in oldSock:
                dirs.remove(sock)

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
        hostname = socket.gethostname()

        # if m.redis is setting in /etc/hosts 
        # then fetch it or set it to empty redisIp
        try:
            redisIp = socket.gethostbyname('m.redis')
            hosts = "--add-host m.redis:{0}".format(redisIp)
        except:
            hosts = ""

        dockerRun = "docker run -d --privileged -v /etc/localtime:/etc/localtime \
                    -v /var/run/durian/{0}:/var/run/durian -v /var/log/php-fpm:/var/log/php-fpm \
                    -v /home/durian:/home/durian -v /dev/shm:/dev/shm --name fpm{0} \
                    {2} --hostname {1}_fpm fpm_2".format(a, hostname, hosts)

        print "running fpm{0}".format(a)
        proc = subprocess.Popen([dockerRun], stdout=subprocess.PIPE, shell=True)

    '''
    create the same amount of containers
    and redirect the request to newer containers but keep old containers
    '''
    def rolling_update(self):
        oldDirs = os.listdir('/var/run/durian')

        for i in range(len(oldDirs)):
            self.create_container()
            time.sleep(2)

        # rename the older container
        for i in oldDirs:
            dockerRename = "docker rename fpm{0} fpm_old{0}".format(i)
            print dockerRename
            subprocess.Popen([dockerRename], stdout=subprocess.PIPE, shell=True)

        self.renew_nginx_setting()

    '''
    restart each fpm container one by one
    before that it will offline it from nginx
    '''
    def rolling_update_one_by_one(self):
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

    '''
    Running nginx container
    expected function: 1.check wether nginx already exist or not
    '''
    def run_nginx_container(self):
        hostname = socket.gethostname()
        nginxRun = "docker run -d --privileged -v /dev/shm:/dev/shm -v /home/durian:/home/durian -v /etc/localtime:/etc/localtime -v /var/log/nginx:/var/log/nginx -v /var/run/durian:/var/run/durian -v /etc/nginx/conf.d:/etc/nginx/conf.d --name nginx --hostname {0}_nginx nginx_2".format(hostname)

        print "Running nginx..."
        proc = subprocess.Popen([nginxRun], stdout=subprocess.PIPE, shell=True)
