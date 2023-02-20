#!/usr/bin/python3
from jenkins import Jenkins, JenkinsError, Job, Server
# http://jenkins-webapi.readthedocs.org/en/latest/
import time
from sys import exit
from configparser import RawConfigParser

config = RawConfigParser()
config.read('config.ini')

jenkins_url = config.get('JENKINS','server_url')
username = config.get('JENKINS','username')
password = config.get('JENKINS','password')

def ctlrl_press():
	print('Exit program')
	exit()
	

try:
	#Jenkins connection
	j = Jenkins(jenkins_url, username, password, verify='chain.crt')
except KeyboardInterrupt: 
	ctlrl_press()
count = 0
six_months_ago = (time.time() - 15768000)
for jobname in j.jobnames:
	job = j.job(jobname)
	try:
		if j.job_exists(jobname):
			if job.last_build.info['timestamp']:
				# Jenkins appears to add microseconds to the timestamp.
				epoch_time = job.last_build.info['timestamp'] / 1000
				if epoch_time < six_months_ago:
					count += 1
					print('{}: {}'.format(count, jobname))
	except KeyboardInterrupt: 
		ctlrl_press()
	except:
		continue

