#!/usr/bin/python

import os
import time
import bsddb
import requests
import json
import binascii
from apscheduler.scheduler import Scheduler

data = bsddb.btopen('netstat_monitor.db', 'c')

AGGREGATOR_URL='http://localhost:9587'
WHITELIST_NETWORKS=(('192.168.0.0', '255.255.255.0'))
PROBE_INTERVAL=2	#10
SEND_INTERVAL=10	#600
MIN_HITS_TO_SEND=10	#entries with less than this value per SEND_INTERVAL won't be sent (each probe interval can generate 1 or more hits)
READ_CONNECTIONS_TIMEOUT=3	#not implemented

PROC_TCP = "/proc/net/tcp"
PROC_TCP6 = "/proc/net/tcp6"

def _load():
    ''' Read the table of tcp connections & remove header  '''
    with open(PROC_TCP,'r') as f:
        content = f.readlines()
        content.pop(0)

    return content

def _load6():
    ''' Read the table of tcp6 connections & remove header  '''
    with open(PROC_TCP6,'r') as f:
        content = f.readlines()
        content.pop(0)

    return content

def _remove_empty(array):
    return [x for x in array if x !='']

def netstat():
    content=_load()
    content.extend(_load6())
    result = []
    for line in content:
        line_array = _remove_empty(line.split(' '))
        l_host,l_port = array.split(':')
        r_host,r_port = array.split(':')
        state = line_array[3]

        nline = (l_host, l_port, r_host, r_port, state)
        result.append(nline)

    return result

def canonical_conn_key(conn):
	return '_'.join(sorted([conn[0], conn[2]])) + '_' + conn[4]

#currently not implemented
def whitelisted(ip):
	return True

def httpPost(url, data):
	headers = {'Content-type': 'application/json'}
	r = requests.post(url, data=json.dumps(data), headers=headers)

	print r.status_code
	


cleanData = False

sched = Scheduler()


@sched.interval_schedule(seconds=SEND_INTERVAL)
def send():
	data_tmp={}
	for (key,value) in data.items():
		if value >= MIN_HITS_TO_SEND:
			data_tmp[key]=value

	cleanData = True

	print "sending..."
	httpPost(AGGREGATOR_URL, data_tmp)


@sched.interval_schedule(seconds=PROBE_INTERVAL)
def probe():
	global data

	print "probing..."
	for conn in netstat():
		if whitelisted(conn[0]) or whitelisted(conn[2]):
			if canonical_conn_key(conn) not in data:
				data[canonical_conn_key(conn)]='0'
				
			data[canonical_conn_key(conn)]=str(int(data[canonical_conn_key(conn)]) + 1)

	if cleanData:
		data = {}


if __name__ == '__main__':
	os.nice(15)

	sched.start()

	while True:
		time.sleep(10)

