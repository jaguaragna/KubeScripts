#!/usr/bin/env python3

import sys 
import subprocess
import argparse
import time
import logging

class EtcdNode:
	def __init__(self,pod,status):
		self.pod=pod
		self.array=status.split(',')
		self.uid=self.array[1].strip()
		self.role=self.array[4].strip()
		self.endpoint=self.array[0].strip()
		self.header=['pod','uid','leader','endpoint']

	def print(self):
		return self.pod+" "+self.uid+" "+self.role+" "+self.endpoint

	def tab(self):
		return [self.pod,self.uid,self.role,self.endpoint]

	def get_uid(self):
		return self.uid	

	def get_pod(self):
		return self.pod	

	def get_endpoint(self):
		return self.endpoint	

	def get_header(self):
		return self.header

	def is_leader(self):
		if self.role == 'true':
			return True 
		return False


# globasl variables
etcdpods=[]
pod=''
BashEtcCmd="kubectl -n kube-system exec "
BashEtcdEndPoint=""
BashEtcdEndPointlist=""
# logging.basicConfig(format='[%(levelname)s]-%(asctime)s- %(message)s', datefmt='%d/%m/%Y %H:%M:%S',stream=sys.stdout, level=logging.DEBUG)
logging.basicConfig(format='[%(levelname)s]-%(asctime)s- %(message)s', datefmt='%d/%m/%Y %H:%M:%S',stream=sys.stdout)

def add_debug(message):
	logging.debug(message)

def get_endpoints():
	endpoints=[]
	BashPods="kubectl -n kube-system get pod -l component=etcd --no-headers -o custom-columns=NAME:.metadata.name |head -n 1"
	BashMember=" -- sh -c \"ETCDCTL_ENDPOINTS='https://127.0.0.1:2379' ETCDCTL_CACERT='/var/lib/rancher/rke2/server/tls/etcd/server-ca.crt' ETCDCTL_CERT='/var/lib/rancher/rke2/server/tls/etcd/server-client.crt' ETCDCTL_KEY='/var/lib/rancher/rke2/server/tls/etcd/server-client.key' ETCDCTL_API=3 etcdctl member list\""
	global BashEtcdEndPoint
	global BashEtcdEndPointlist
	global pod


	add_debug('BashEtcdMembers command: '+BashPods)

	# get etcd pod
	pod=kube_exec(BashPods).strip()

	# get etcd member with external ip
	BashEtcdMembers=BashEtcCmd+pod+BashMember
	add_debug('BashEtcdMembers command: '+BashEtcdMembers)

	#construct etcd endpoint list
	for elem in kube_exec(BashEtcdMembers).split('\n'):
		if elem:
			line=elem.split(',')
			endpoints.append(line[4].strip())

	BashEtcdEndPoint="ETCDCTL_ENDPOINTS='"+','.join(endpoints)+"' " 
	BashEtcdEndPointlist="'"+','.join(endpoints)+"' "

	add_debug('BashEtcdEndPoint command: '+BashEtcdEndPoint)

def migrate_leader(newleader):

	leader=[]
	# bug wuth etcd version 3.4.3 for move leader env variable not accepted need to pass command this way 
	# etcdctl --endpoints XXXX --cacert XXX --cert XXX --key XXX move-leader ${transferee_id}
	bashEtcdMigrate=" -- sh -c \"etcdctl --cert /var/lib/rancher/rke2/server/tls/etcd/server-client.crt --key /var/lib/rancher/rke2/server/tls/etcd/server-client.key --cacert  /var/lib/rancher/rke2/server/tls/etcd/server-ca.crt --endpoints="+BashEtcdEndPointlist+"move-leader "


	# message='Testing migration with : '+newleader
	logging.debug('Testing migration with : '+newleader)
	
	# get pods to iterate through
	get_etcdpods()
	
	for pod in etcdpods:
		if newleader.strip() in pod.tab():
			add_debug('Checking migration for  : '+pod.print())

			if pod.is_leader():
				print('Node is already Leader no action required')
				sys.exit(2)
			newleadpod=pod.get_pod()
			print("Migratig leader to : ",newleadpod)
			leader=pod.tab()
			bashEtcdEndpoints=get_endpoints()
			bashMigrateAll=BashEtcCmd+newleadpod+bashEtcdMigrate+pod.get_uid()+"\""
			add_debug('bashMigrateAll command: '+bashMigrateAll)
			kube_exec(bashMigrateAll)
	if leader:
		print('Refreshing etcd nodes list ...')
		time.sleep(3)
		list_nodes_state()
	else:
		print('No UID or pod corresponding to '+newleader)

def kube_exec(command):
	result = subprocess.run(
	    ["/bin/zsh", "-c", command, ],capture_output=True,text=True
	)
	return result.stdout

def get_etcdpods():
	global etcdpods
	#create node to ip list
	BashListNodes="kubectl -n kube-system get pod -l component=etcd  -o custom-columns=\"POD-NAME\":.metadata.name,\"IP\":.status.hostIP --no-headers"
	add_debug('BashListNodes command: '+BashListNodes)
	
	liste=[]
	for line in kube_exec(BashListNodes).split('\n'):
		if line:
			liste.append(line.split())
	
	if not liste:
		print('No nodes retrieve')
		sys.exit(4)

	add_debug(liste)

	BashEtcdEndPointStatus1=" -- sh -c \""
	BashEtcdEndPointStatus2="ETCDCTL_CACERT='/var/lib/rancher/rke2/server/tls/etcd/server-ca.crt' ETCDCTL_CERT='/var/lib/rancher/rke2/server/tls/etcd/server-client.crt' ETCDCTL_KEY='/var/lib/rancher/rke2/server/tls/etcd/server-client.key' ETCDCTL_API=3 etcdctl endpoint status\""
	BashEtcdEndPointStatus=BashEtcCmd+pod+BashEtcdEndPointStatus1+BashEtcdEndPoint+BashEtcdEndPointStatus2
	
	add_debug('BashEtcdEndPointStatus command: '+BashEtcdEndPointStatus)
	add_debug(kube_exec(BashEtcdEndPointStatus))

	lines=kube_exec(BashEtcdEndPointStatus).split('\n')
	lines.remove('')

	# construct object etc node with endpojt and pod name with node in it
	add_debug('Object pod connstruction')
	for line in lines:
		for elem in liste:
			if liste:
				if elem[1] in line:
				 	etcpod=EtcdNode(elem[0],line)
				 	add_debug(etcpod.print())
				 	etcdpods.append(etcpod)
				 	break

def list_nodes():
	get_etcdpods()
	tableformat="{:1} {:18} {:18} {:7} {:20}"

	#Print table
	print(tableformat.format("", *etcdpods[0].get_header()))
	print('-'*78)
	for etcpod in etcdpods:
		print(tableformat.format("", *etcpod.tab()))

def list_nodes_state():
	# bash command to execute
	BashEtcdEndPointStatus1=" -- sh -c \""
	BashEtcdEndPointStatus2="ETCDCTL_CACERT='/var/lib/rancher/rke2/server/tls/etcd/server-ca.crt' ETCDCTL_CERT='/var/lib/rancher/rke2/server/tls/etcd/server-client.crt' ETCDCTL_KEY='/var/lib/rancher/rke2/server/tls/etcd/server-client.key' ETCDCTL_API=3 etcdctl endpoint status --write-out table\""
	
	BashEtcdEndPointStatus=BashEtcCmd+pod+BashEtcdEndPointStatus1+BashEtcdEndPoint+BashEtcdEndPointStatus2
	add_debug('BashEtcdEndPointStatus command: '+BashEtcdEndPointStatus)

	print(kube_exec(BashEtcdEndPointStatus))


def get_leader():
	get_etcdpods()
	for pod in etcdpods:
		add_debug('Check leader for :'+pod.print())
		if pod.is_leader():
			print("leader is : "+pod.print())
			break

def cli_management():
    # argument pass to the application
    parser = argparse.ArgumentParser( 
        prog="etcd-management",
        description="Manage etcd rke2 pods",
        epilog="Have a good day ;) ")

    parser.add_argument("-v", "--verbose", help='Add debug information',action='store_true')
    #group to mutually exclude arguments
    req = parser.add_mutually_exclusive_group(required=True)
    req.add_argument("-l", "--list",help='List etcd pods information',action='store_true')
    req.add_argument("-s", "--state",help='List etcd node state',action='store_true')
    req.add_argument("-g", "--leader", help='Get etcd leader pod',action='store_true')
    req.add_argument("-m", "--migrate",nargs="?", help='Migrate etcd leader to pod or pod uid',action='store')

    args = parser.parse_args()

    return args

def main():
	# mange cli arguments
	args=cli_management()

	# get etcd endpoints
	get_endpoints()
	
	if args.verbose:
		#Activate logging
		logger= logging.getLogger()
		logger.setLevel('DEBUG')

		logger.debug('debug ON')

	if args.state:
		list_nodes_state()

	if args.list:
		list_nodes()

	if args.leader:
		get_leader()

	if args.migrate:
		migrate_leader(args.migrate)


if __name__ == "__main__":
    main()
