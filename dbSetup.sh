#!/bin/bash


#####
#
# This script should be ran to setup the initial procSpy database. Not much use
# after that.
#
####

C_RESET='\033[0m'
C_RED='\033[1;31m'
C_GREEN='\033[1;32m'
C_YELLOW='\033[1;33m'
C_GRAY='\033[1;37m'
C_BLUE='\033[1;34m'
GREEN_PLUS="${C_GREEN}[+]${C_RESET}"
RED_MINUS="${C_RED}[-]${C_RESET}"
YELLOW_EX="${C_YELLOW}[!]${C_RESET}"
BLUE_QUE="${C_BLUE}[?]${C_RESET}"


#script must be ran as root.
if [ ! $(id -u) -eq 0 ]; then

	echo -e "${RED_MINUS} ERROR: The Database Setup script must be ran as root."	
	exit 1
fi

#checks mysql is running.
if [ ! $(systemctl is-active --quiet mysql) -eq 0 ]; then

	echo -e "${RED_MINUS} mySQL doesn't appear to be running. Make sure mysql service is running."
	exit 1
fi


echo -e "${YELLOW_EX} By default, procSpy will create a new mysql user that will be used to interact"
echo -e "${YELLOW_EX} with the database when running procSpy in database mode."
while true; do

	echo -en "${BLUE_QUE} Would you like to specify a different mysql user instead? (y/n): "
	read diffUser

	if [ "$diffUser" == "y" ] || [ "$diffUser" == "Y" ]; then

		echo -en "${BLUE_QUE} Please specify the MySQL ${GRAY_B}username${RESET}: "
        read mySQLUser

        echo -en "${BLUE_QUE} Please specify the MySQL ${GRAY_B}password${RESET}: "
        read mySQLPass

		break

	elif [ "$diffUser" == "n" ] || [ "$diffUser" == "N" ]; then
	
		mySQLUser="procspy"

		#generates a random password
		mySQLPass="$(head /dev/urandom | tr -dc A-Za-z0-9 | head -c $(echo $((5 + RANDOM % 10))))"

		break

	else

		echo -e "${RED_MINUS} Invalid response. Please specify 'y' or 'n'."

	fi
done


if [ -e ./procSpyDb.cfg ]; then

	echo -e "${YELLOW_EX} It looks like you already have database configurations."
	while true; do
	
		echo -en "${BLUE_QUE} Would you like to overwrite this configuration? (y/n): "
		read overwrite

		if [ "$overwrite" == "y" ] || [ "$overwrite" == "Y" ]; then	
			break

		elif [ "$overwrite" == "n" ] || [ "$overwrite" == "N" ]; then
			echo -en "${YELLOW_EX} Leaving current configuration and exiting . . ."
			exit 1
		else
			echo -e "${RED_MINUS} Invalid response. Please specify 'y' or 'n'."

		fi
	done
fi


echo "[mySQL]" > ./procSpyDb.cfg
echo "MYSQL_USER=${mySQLUser}" >> ./procSpyDb.cfg
echo "MYSQL_PASS=${mySQLPass}" >> ./procSpyDb.cfg
echo "MYSQL_DB=ProcSpy" >> ./procSpyDb.cfg
echo "MYSQL_HOST=127.0.0.1" >> ./procSpyDb.cfg
echo -e "${GREEN_PLUS} Config file created . . ."


createDB="CREATE DATABASE IF NOT EXISTS ProcSpy;"
createUser="GRANT ALL PRIVILEGES ON ProcSpy.* TO '${mySQLUser}'@'localhost' IDENTIFIED BY '${mySQLPass}';"
createTable="CREATE TABLE IF NOT EXISTS ProcSpy.proc_history (id int unsigned not null auto_increment, \
			 pid int not null, ppid int not null, uid int not null, user VARCHAR(20) not null, \
		     cmd VARCHAR(8000) not null, start_time TIMESTAMP not null, end_time TIMESTAMP NULL, PRIMARY KEY (id));"

mysql -Bse "${createDB}"
mysql -Bse "${createUser}"
mysql -Bse "${createTable}"
echo -e "${GREEN_PLUS} mySQL Database created. You should be good to run in database mode now."




	
		





