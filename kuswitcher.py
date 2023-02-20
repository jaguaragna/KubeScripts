#!/usr/local/bin/python3
#aws account selector
import subprocess
import inquirer
import os

#Command tro retrieve amazon accounts
cmd="awk '{print $1}' ~/.kube/kube.list"

p=subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True,universal_newlines=True)
output=p.communicate()[0]

questions = [
    inquirer.List('cluster',
                  message="Choose your cluster",
                  choices=output.split(),
                  ),
]
answers=inquirer.prompt(questions)
# add to correctly handle ctrl + c
if answers is None:
    exit()
else:
    cmd="grep "+answers['cluster']+" ~/.kube/kube.list|awk '{print $2}'"
    p1=subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True,universal_newlines=True)
    kubeconfig=p1.communicate()[0]
    print(kubeconfig)
#get user home directory and create env variable
homedir = os.path.expanduser('~')
direct=homedir+"/.zshrc.kube"
f= open(direct,"w+")
f.write("export KUBECONFIG="+kubeconfig)
f.close()
os.system("/bin/zsh")
