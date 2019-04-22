#!/usr/bin/env python3


from os import listdir
from os import stat
from time import sleep
import grp
import pwd
import sys
import argparse

try:
	import mysql.connector
except ImportError:
	pass

from datetime import datetime
from collections import namedtuple

DEAD_PROC = "I am dead and this is sad"
SKY_IS_BLUE = True
PROC_DIR = "/proc"
PROC_DEAD = "DEADPROC"
PROCESS = namedtuple('PROCESS', 'pid ppid uid user cmdline timestamp')

MODE_STDOUT = "stdout"
MODE_DB = "mysql"
MODE_FILE = "file"

C_RESET = '\033[0m'
C_RED = '\033[1;31m'
C_GREEN = '\033[1;32m'
C_GRAY = '\033[1;37m'
GREEN_PLUS = f"{C_GREEN}[+]{C_RESET}"
RED_MINUS = f"{C_RED}[-]{C_RESET}"


def getProcData(pid):

	proc_subdir = f'{PROC_DIR}/{str(pid)}'
	try:
		filestats = stat(proc_subdir)
		ownerUid = filestats.st_uid
		timestamp = filestats.st_ctime
		ownerName = pwd.getpwuid(ownerUid)[0]
		with open(f'{proc_subdir}/cmdline', 'r') as fl:

			#cmdline uses \00 for string separation, so we must replace those with spaces
			cmds = fl.read().replace("\00", ' ').strip()

		with open(f'{proc_subdir}/stat', 'r') as fl:
			ppid = int(fl.read().split()[3])

		
		if len(cmds) > 0:
			return PROCESS(pid=pid, ppid=ppid, uid=ownerUid, user=ownerName, cmdline=cmds, timestamp=timestamp)

		else:
			return DEAD_PROC

	#sometimes the process will die as files are being read - this keeps everything alive if that happens
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
	
	writeString = f'{timestamp}:{procData.pid}:{procData.ppid}:{procData.uid}:{procData.user}:{procData.cmdline}'
	
	with open(outfile, 'a') as f:
		f.write(writeString + '\n')

def writeDeadProcs(pid, outfile):
	
	timestamp = datetime.now()
	
	writeString = f'{timestamp}:{str(pid)}:{PROC_DEAD}'

	with open(outfile, 'a') as f:
		f.write(writeString + '\n')


def dbAddProc(procData):

	timestamp = datetime.now()

	db = mysql.connector.connect( user="procspy",
		        	      password="procspy",
			              host="127.0.0.1",
				      database="ProcSpy"
		     			 )	
	
	cursor = db.cursor()

	pid = procData.pid
	ppid = procData.ppid
	uid = procData.uid
	user = procData.user
	cmd = procData.cmdline

	query = ( "INSERT INTO proc_history "
		  "(pid, ppid, uid, user, cmd, start_time)"
	          "VALUES (%s, %s, %s, %s, %s, %s)" )

	data = ( pid, ppid, uid, user, cmd, timestamp )

	cursor.execute(query, data)
	
	db.commit()
	cursor.close()
	db.close()

def dbTermProc(pid):

	timestamp = datetime.now()

	db = mysql.connector.connect( user="procspy",
		        	      password="procspy",
			              host="127.0.0.1",
				      database="ProcSpy"
		     			 )	


	cursor = db.cursor()

	query = ( "SELECT id FROM proc_history WHERE pid=%s")
	data = (pid,)

	cursor.execute(query, data)
	try:
		db_id = cursor.fetchall()[0][0]
		print(db_id)
	except IndexError:
		return None


	query = ( "UPDATE proc_history SET end_time = %s WHERE id=%s AND end_time IS NULL" )
	data = (timestamp, db_id)

	cursor.execute(query, data)

	db.commit()
	cursor.close()
	db.close()

		
	
	


def main():

	parser = argparse.ArgumentParser()
	parser.add_argument('--modes', nargs='?', help='Specifies mode to output commands')
	parser.add_argument('-o', nargs='?', help='Specifies the output file in file mode')
	parser.add_argument('-u', nargs='?', help="Username for database mode.")
	parser.add_argument('-p', nargs='?', help="Password for database mode.")
	parser.add_argument('-d', nargs='?', help="Password for database mode.")

	args = parser.parse_args()

	deployment_modes = args.modes
	deployments = deployment_modes.split(",")
	
	mode_stdout = False
	mode_file = False
	mode_db = False
	for i in deployments:
		valid = False
		if i.strip() == MODE_FILE:
			mode_file = True
			valid = True
		if i.strip() == MODE_DB:
			mode_db = True
			valid = True
		if i.strip() == MODE_STDOUT:
			mode_stdout = True
			valid = True

		if not valid:
			print("Invalid mode(s) Selected. Please use '-h' for usage.")
			sys.exit(1)
		
	
	if mode_file and not args.o:
		print("An output file must be specified when using file mode.")
		sys.exit(1)

	if mode_db and not (args.u or args.p or args.d):
		print("Insufficient information provided for database mode.")
		sys.exit(1)

	#initializes pids. This will be used as a baseline, and any newly added
	#processes will be recorded.
	initialPids = getPids()
	sleep(3)

	while SKY_IS_BLUE:
		
		newPids = getPids()
		pidDiffs = getPidDiscrepancies(initialPids, newPids)

		
		for i in pidDiffs['SPAWNED_PIDS']:
			
			procDat = getProcData(i)
			if procDat != DEAD_PROC :

				if mode_stdout:

					strout = f"{GREEN_PLUS} [{datetime.now()}] [PID:{procDat.pid} PPID:{procDat.ppid}] "
					strout += f"{procDat.user} ({procDat.uid}): {C_GRAY}{procDat.cmdline}{C_RESET}"
					print(strout)
		
					
				if mode_file:
		
					outputFile = args.o
					writeNewProcs(procDat, outputFile)

				if mode_db:
					dbAddProc(procDat)

		
		for i in pidDiffs['KILLED_PIDS']:


			if mode_stdout:
				strout = f"{RED_MINUS} [{datetime.now()}] PID {i} has terminated."
				print(strout)

			if mode_file:
			
				outputFile = args.o
				writeDeadProcs(i, outputFile)

			if mode_db:
				# we need to send in the cmd just in case of pid reuse.
				dbTermProc(i)

		initialPids = newPids

		sleep(0.5)



main()




