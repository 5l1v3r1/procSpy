CREATE DATABASE IF NOT EXISTS ProcSpy;
GRANT ALL PRIVILEGES ON ProcSpy.* TO 'procspy'@'localhost' IDENTIFIED BY 'procspy';
USE ProcSpy;
CREATE TABLE IF NOT EXISTS proc_history (id int unsigned not null auto_increment, pid int not null, ppid int not null, uid int not null, user VARCHAR(20) not null, cmd VARCHAR(8000) not null, start_time TIMESTAMP not null, end_time TIMESTAMP NULL, PRIMARY KEY (id));
