#!/usr/bin/env python3

import mysql.connector
import argparse
import sys
from os import path


MODE_FILE = 'file'
MODE_DB = 'db'

C_RESET = '\033[0m'
C_RED = '\033[1;31m'
C_GREEN = '\033[1;32m'
C_GRAY = '\033[1;37m'
GREEN_PLUS = f"{C_GREEN}[+]{C_RESET}"
RED_MINUS = f"{C_RED}[-]{C_RESET}"



def parseFile(filename):

	





def main():

	parser = argparse.ArgumentParser()
	parser.add_argument('--mode', nargs='?', help='Specifies the mode to parse data from')
	parser.add_argument('-a', action='store_true', help='Displays the entire command history')
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
		
		mode = modeArg

	elif modeArg == MODE_DB:
		mode = modeArg

	else:
		print(f"{RED_MINUS} Invalid Mode Specified. Please state 'file' or 'db'")
		sys.exit(1)


		
		



main()		
