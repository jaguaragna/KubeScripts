#!/usr/bin/python3

#aws account selector
import subprocess
import inquirer
import os
from sys import exit
from platform import python_version


print("Current Python Version-", python_version())
#Command tro retrieve amazon accounts
#cmd="grep '\[' ~/.aws/config |sed -e 's/\[//g' -e 's/\]//g'"
cmd="grep '\[' ~/.aws/config |sed -e 's/\[//g' -e 's/\]//g'|sed -e 's/profile //g'"
p=subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True,universal_newlines=True)
output=p.communicate()[0]
questions = [
    inquirer.List('aws',
                message="Choose your account",
                choices=output.split(),
                ),
]
answers=inquirer.prompt(questions)
if answers is None:
    exit()
#get user home directory and create env variable
homedir = os.path.expanduser('~')
direct=homedir+"/.zshrc.aws"
f= open(direct,"w+")
f.write("export AWS_PROFILE="+answers['aws'])
f.close()
os.system("/bin/zsh")
