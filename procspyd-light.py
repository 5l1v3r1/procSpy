#!/usr/bin/env python3


from os import listdir
from os import stat
from os import path
from time import sleep
import grp
import pwd
import sys
import argparse
from datetime import datetime
from collections import namedtuple

DEAD_PROC = "I am dead and this is sad"
SKY_IS_BLUE = True
PROC_DIR = "/proc"
PROC_DEAD = "DEADPROC"
PROCSPY_FILE_INIT = "PROCSPY_FILE_HEADER"
PROCESS = namedtuple('PROCESS', 'pid ppid uid user cmdline timestamp')


def getProcData(pid):

	proc_subdir = PROC_DIR + '/' + str(pid)
	try:
		filestats = stat(proc_subdir)
		ownerUid = filestats.st_uid
		timestamp = filestats.st_ctime
		ownerName = pwd.getpwuid(ownerUid)[0]
		with open(proc_subdir + '/cmdline', 'r') as fl:

			cmds = fl.read().replace("\00", ' ').strip()

		with open(proc_subdir + '/stat', 'r') as fl:
			ppid = int(fl.read().split()[3])

		
		if len(cmds) > 0:
			return PROCESS(pid=pid, ppid=ppid, uid=ownerUid, user=ownerName, cmdline=cmds, timestamp=timestamp)

		else:
			return DEAD_PROC

	except FileNotFoundError:
		
		return DEAD_PROC

def getPids():

	
	procDirList = listdir(PROC_DIR)
	pidList = []

	for i in procDirList:
		
		try:
			pidList.append(int(i))
		except ValueError:
			pass
			
			
	
	return pidList


def getPidDiscrepancies(oldPids, newPids):

	pidDiffs = { 'KILLED_PIDS' : [],
		     'SPAWNED_PIDS' : []
		}


	for pid in oldPids:
		if pid not in newPids:
			pidDiffs['KILLED_PIDS'].append(pid)

	for pid in newPids:
		if pid not in oldPids:
			pidDiffs['SPAWNED_PIDS'].append(pid)

	return pidDiffs


def writeNewProcs(procData, outfile):

	timestamp = datetime.now()
	
	writeString = str(timestamp) + ':::' + str(procData.pid) + ':::' + str(procData.ppid) + ':::' + str(procData.uid) + ':::' + procData.user + ':::' + procData.cmdline
	
	with open(outfile, 'a') as f:
		f.write(writeString + '\n')


def writeDeadProcs(pid, outfile):
	
	timestamp = datetime.now()
	
	writeString = str(timestamp) + ':::' + str(pid) + ':::' + PROC_DEAD

	with open(outfile, 'a') as f:
		f.write(writeString + '\n')


def runCycle(initialPids, outputFile="psout.log"):

	while True:

		newPids = getPids()
		pidDiffs = getPidDiscrepancies(initialPids, newPids)

		
		for i in pidDiffs['SPAWNED_PIDS']:
			
			procDat = getProcData(i)
			if procDat != DEAD_PROC :

					writeNewProcs(procDat, outputFile)


		
		for i in pidDiffs['KILLED_PIDS']:
			
				writeDeadProcs(i, outputFile)


		initialPids = newPids

		sleep(0.5)


parser = argparse.ArgumentParser()
parser.add_argument('-o', nargs='?')
args = parser.parse_args()

try:

	initialPids = getPids()
	sleep(3)
	if not args.o:
		runCycle(initialPids)

	else:
		runCycle(initialPids, args.o)

except KeyboardInterrupt:
	print("Gracefully Exiting . . .")
	sys.exit(1)
