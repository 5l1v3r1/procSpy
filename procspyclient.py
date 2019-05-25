#!/usr/bin/env python3

import argparse
import sys
from os import path
from collections import namedtuple


MODE_FILE = 'file'
MODE_DB = 'db'

DB_CFG_FILE = './procSpyDb.cfg'
PROCSPY_FILE_INIT = "PROCSPY_FILE_HEADER"

PROCESS = namedtuple('PROCESS', 'pid ppid uid user cmdline starttime endtime')
PROC_DEAD = "DEADPROC"

C_RESET = '\033[0m'
C_RED = '\033[1;31m'
C_GREEN = '\033[1;32m'
C_GRAY = '\033[1;37m'
C_YELLOW = '\033[1;32m'
GREEN_PLUS = f"{C_GREEN}[+]{C_RESET}"
RED_MINUS = f"{C_RED}[-]{C_RESET}"


def parseFile(filename):

	procs = []

	with open(filename, 'r') as f:
		lineList = f.readlines()	

	deadProcs = []
	for line in lineList:
		
		if PROC_DEAD in line:
			deadProcs.append(line.split(":::"))


	for line in lineList:
		
		if PROC_DEAD not in line:

			lineData = line.split(":::")
			starttime = lineData[0].strip()
			pid = int(lineData[1].strip())
			ppid = int(lineData[2].strip())
			uid = int(lineData[3].strip())
			user = lineData[4].strip()
			cmd = lineData[5].strip()

			endtime = "NULL"
			for i in deadProcs:
				if int(i[1]) == pid:
					endtime = i[0]

			procs.append(PROCESS(pid=pid, ppid=ppid, uid=uid, user=user, cmdline=cmd, starttime=starttime, endtime=endtime))


	return procs


def parseDb():


	procs = []
	config = configparser.ConfigParser()
	config.read(DB_CFG_FILE)

	try:
		cfgData = config["mySQL"]
	except:
		print("{RED_MINUS} There appears to be some problems with your Database config file.")
		sys.exit(1)


	user = cfgData["MYSQL_USER"]
	passwd = cfgData["MYSQL_PASS"]
	database = cfgData["MYSQL_DB"]
	host = cfgData["MYSQL_HOST"]

	db = mysql.connector.connect( user=user, password=passwd, host=host, database=database )

	cursor = db.cursor()

	
	query = ( "SELECT * FROM proc_history WHERE 1=1;" )

	cursor.execute(query)

	for ( db_id, pid, ppid, uid, user, cmd, starttime, endtime ) in cursor:
		
		procs.append(PROCESS(pid=pid, ppid=ppid, uid=uid, user=user, cmdline=cmd, starttime=starttime, endtime=endtime))


	return procs
		

	



	


def processFilters(processes, args):

	outProcs = processes

	# indicates user just wants all processes
	if args.all:
		return outProcs

	if args.user:
		i = 0
		while i < len(outProcs):
			proc = outProcs[i] 
			if proc.user != args.user:
				del outProcs[i]
			else:
				i += 1

	if args.cmd:
		i = 0
		while i < len(outProcs):
			proc = outProcs[i]
			if args.cmd not in proc.cmdline:
				del outProcs[i]
			else:
				i += 1

	if args.uid:
		i = 0
		while i < len(outProcs):
			proc = outProcs[i] 
			if proc.uid != int(args.uid):
				del outProcs[i]
			else:
				i += 1


	return outProcs


def printPretty(proc):

	starttime = str(proc.starttime).split(".")[0]
	try:
		endtime = str(proc.endtime).split()[1].split(".")[0]
	except:
		endtime = "NULL"
	print(f"User {C_GRAY}{proc.user}{C_RESET} ({proc.uid}): ", end="")
	print(f"""{starttime} -> {endtime}: {C_GRAY}{proc.cmdline}{C_RESET} ({proc.pid}, parent {proc.ppid})""")
	


parser = argparse.ArgumentParser()
parser.add_argument('--mode', nargs='?', help='Specifies the mode to parse data from')
parser.add_argument('--all', action='store_true', help='Displays the entire command history')
parser.add_argument('--user', nargs='?', help='Query history for commands ran by certain user.')
parser.add_argument('--uid', nargs='?', help='Query history for commands ran under a certain uid')
parser.add_argument('--cmd', nargs='?', help='Query history for commands containing specified string')
parser.add_argument('-s', nargs='?', help='Source file for file mode.')


args = parser.parse_args()
modeArg = args.mode
mode = ""
	
if modeArg == MODE_FILE:

	if not args.s:
		print(f"{RED_MINUS} No source file specified. Please specify a source file with '-s'")
		sys.exit(1)

	elif args.s:
		fileExists = path.isfile(args.s)
		if not fileExists:
			print(f"{RED_MINUS} Specified file could not be located. Please specify a valid procSpy file.")
			sys.exit(1)

			
		procList = parseFile(args.s)
		parsedProcs = processFilters(procList, args)
		for i in parsedProcs:
			printPretty(i)
				


elif modeArg == MODE_DB:

	# only import if necessary
	import mysql.connector
	import configparser

	cfgExists = path.isfile(DB_CFG_FILE)
	if not cfgExists:
                print(f"{RED_MINUS} It looks like database mode has not been set up on this system (config file missing).")
                print(f"{RED_MINUS} Please run the dbSetup.sh script to use database mode.")
                sys.exit(1)

	else:
		procList = parseDb()
		parsedProcs = processFilters(procList, args)
		for i in parsedProcs:
			printPretty(i)


	



else:
	print(f"{RED_MINUS} Invalid Mode Specified. Please state 'file' or 'db'")
	sys.exit(1)

