##
# @mainpage
# Copycat is a python script designed to work as a supervisor of the whole system with the task of copy the file when it becomes necessary. 
# The copy became necessary when client ask for a file more than N time in the last X hours.
# To work copycat needs a configuration file, called server_list.txt, where are stored some information in this way:
# server_ip\log_name client_username1\nearest_server_ip-client_username2\nearest_server_ip...
# 
# In this way is possible to know which clients are connected to a specific server an for wach one is possible to know which is the nearest server.
# 
# To explain how the script works is better to analyze it throw a few steps.
#
# **STEP ONE:**
#
# First of all, the script will read line by line from the file and, for every server, it will create some object Mover identified by 
# two tuple <Analyzed server, Log name>, <Client username, Client nearest server>-<Client2 username, Client2 nearest server> - and so on.
# Each of this object is a thread which allows the analysis to run in parallel ensuring a much faster and efficient computation time.
#
# **STEP TWO:**
#
# Each thread will connect to the database throw a dedicated classis. Throw this connection the script will get all the request made from a specific client to a specific server in the last X hours. 
# The script will then count how many times every file has been requested, if this has happened more than 3 times then copycat will proceed to move the file.
#
# **STEP THREE:**
#
# If a file needs to be copied the script will create an ftp connection using the ftplib python library. 
# The file will be temporarily stored in local directory and delete immediately after the upload end. 
# All the upload and download operations are handled by a specific class to keep the script scalable and adaptable.
#
#
#
# 
#
#
#
#
#
#
#
#
#
#
#
#
#
#
