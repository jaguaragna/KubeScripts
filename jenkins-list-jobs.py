#!/usr/bin/python3
from jenkins import Jenkins, JenkinsError, Job, Server
# http://jenkins-webapi.readthedocs.org/en/latest/
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


try :
	#Jenkins connection
	j = Jenkins(jenkins_url, username, password, verify='chain.crt')
except KeyboardInterrupt:
	ctlrl_press()

count = 0
for jobname in j.jobnames:
	job = j.job(jobname)
	print('{}'.format(jobname))
	count += 1
print('{} jobs found'.format(count))
