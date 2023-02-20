#!/usr/bin/python3
from jenkins import Jenkins, JenkinsError, Job, Server
from configparser import RawConfigParser
from sys import exit

config = RawConfigParser()
config.read('config.ini')

jenkins_url = config.get('JENKINS','server_url')
username = config.get('JENKINS','username')
password = config.get('JENKINS','password')


def ctlrl_press():
        print('Exit program')
        exit()

#Jenkins connection
try:
	j = Jenkins(jenkins_url, username, password, verify='chain.crt')
except KeyboardInterrupt:
        ctlrl_press()

for jobname in j.jobnames:
	try:
		if j.job_exists(jobname):
			if j.job_enabled(jobname):
				if j.job_last_build(jobname):
					if  not j.job_last_build(jobname) == j.job_last_successful_build(jobname):
			 			print('job: {}'.format(jobname))
	
	except KeyboardInterrupt:
		ctlrl_press()
	except:
		continue
