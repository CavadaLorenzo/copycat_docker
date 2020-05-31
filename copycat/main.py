##
# @file
# The main class. Here is where the script will start
# First of all the script will read from a configuration file the
# list of server with all the connected host.
# For each tuple <server, client> it will create a thread to process it.
#
from flask import Flask
from flask import request
from flask import jsonify
import time, requests, traceback, queue, os
from influxDB_database import InfluxDB_DB
from postgres_database import Postgres_DB
from collections import Counter

try:    MANAGER_IP = os.environ['MANAGER_IP']
except:    MANAGER_IP = '192.168.1.188' 
try:    MANAGER_PORT = os.environ['MANAGER_PORT']
except:    MANAGER_PORT = '7025' 

app = Flask(__name__)

def get_server_from_db():
    """
    Return a list of the server
    """
    db = Postgres_DB()
    return db.get_servers_list()

def get_request_from_db(server, time):
    """
    Return a list of request
    """
    db = InfluxDB_DB()
    return db.select_all_time(time, server['server_id'])

def count_element(result_set):
    """
    This method will count the number of times that every file has been requested. To do that it uses the object Counter from the collections library.
     """
    n_request = []
    for request in result_set:
        request = request['file_path'].split("/")
        n_request.append(request[len(request) - 1])
    n_request = Counter(n_request)
    return n_request.most_common()

@app.route("/")
def copycat():  
    """
    This method will, from a list with 2 FTP servers, check the number of request done to the file
    stored in the first server in the last TIME_SPAN hour. If this number is more than COUNT than proceed
    with the copy to the second server.
    """
    try:

        json_q = queue.Queue() # queue used to return a list of the transfer that have been made
        servers = get_server_from_db() # list of FTP servers present in the system
        from_server = servers[0] # server where the script will check the number of request
        to_server = servers[1] # server where the file will be moved
        request_list = get_request_from_db(from_server, request.args.get('TIME')) # list of all the request done to the first server in the last time span
        n_request = count_element(request_list) # number of time that each file have been requested
        for filename, n in n_request: # here I check if a file has been requested more than COUNT times, if yes the file will be copied to the to_server
            if n >= int(request.args.get('COUNT')):
                print("Mooving file: " + filename + " to server: " + str(to_server['server_id']))
                start = time.time()
                manager = 'http://' + MANAGER_IP + ':' + MANAGER_PORT + '?server_ip=' + to_server['server_ip'] + '&server_port=' + to_server['server_ssh_port'] + '&filename=' + filename
                print(manager)
                check = requests.get(manager).json()
                end = time.time()
                if check['result']:
                    json_q.put({
                        'filename': filename,
                        'from_server': MANAGER_IP,
                        'to_server': to_server['server_id'],
                        'time': str(end - start)
                    })
                    print("File: " + filename + " copied " + "in: " + str(end - start) + " sec")
                else:
                    print("An error occurred during the process of the copy of the file ")
    except requests.exceptions.ConnectionError as ex:
        print(ex.__class__, ex.__class__.__name__)
        print("ConnectionError Exception, maybe the manager is down?")
    except Exception as ex:
        print(ex.__class__, ex.__class__.__name__)
        tb = traceback.format_exc()
        print(tb)
    
    return jsonify({'transfer': list(json_q.queue)})

if __name__ == "__main__":
    """
    The application will listen on the port 4025 waiting for get request to start.
    The request needs 2 parameters: TIME and COUNT. Time will represent the interval of time that
    copycat needs to control (i.e. last 3 hours). Count will represent the number of times that 
    a file needs to have been request to justify the copy from the main server to the server.
    Right now copycat work in an easier version with only two FTP server, the first one is the one
    on which the script will focus checking the request that have been made to him and, in case
    this number will be more than COUNT will perform the copy to the second FTP server.
    """
    app.run(debug=True, host="0.0.0.0", port=4025)
