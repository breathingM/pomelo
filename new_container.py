#!/usr/bin/python
# -*- coding:utf8 -*-
#新建一個container並指定空閒的SOCK位置給它
__author__ = 'jjj'

import os
import subprocess

MAX_CONTAINER_NUM = 5

def get_free_seq():
    dirs = os.listdir('/var/run/durian')
    for i in range(0, MAX_CONTAINER_NUM):
        if str(i) not in dirs:
            return str(i)
        else:
            continue

    print "There is no Space for the new container"
    exit(1)

a = get_free_seq()
dockerRun = "docker run -d -v /var/run/durian/{0}:/var/run/durian --name fpm{0} fpm_2".format(a)
print dockerRun
proc = subprocess.Popen([dockerRun], stdout=subprocess.PIPE, shell=True)
