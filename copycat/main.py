##
# @file
# The main class. Here is where the script will start
# First of all the script will read from a configuration file the
# list of server with all the connected host.
# For each tuple <server, client> it will create a thread to process it.
#
from mover_thread import Mover
from flask import Flask
from flask import request
from flask import jsonify
import queue


app = Flask(__name__)

def get_client_thread(line, color, time, count, queue):
    """
    This method will create and return an array of thread for every server. The script will
    receive a line of the configuration file which is something like that:
    <server_ip, port, server_log> <client1, nearest_s1, port1>-<client_2, nearest_s2, port2>-...
    This method will parse the line and will create N different threads identified
    by a tuple <server, client> where the server is identified by its IP and log_name
    and the client is identified by its name and nearest_server_IP.
    A color is also used to create a more readable console.
    There is also a shared queue between all the threads where they will store all 
    the transfer thet they will perform.
    """
    threads = []
    if line != "":
        line = line.split(" ")
        server = line[0].split("/")
        connected_clients = line[1].split("-")
        for c_client in connected_clients:
            c_client = c_client.split("/")
            threads.append(Mover(server, c_client, color, queue, time, count))

    return threads

@app.route("/")
def copycat():  
    """
    Here is where the script will read each line of the configuration file
    and will start the thread.
    The color of the thread is done using a py library called colored where
    the color can be identify by a number from 0 to 255.
    Each thread will be saved in a thread_lsit whichi will allow the script to 
    access every single thread. This is important because this festure is used
    to make the script wait unitll all the threads are ended. After that the script 
    can return the queue with all the json which represent all the completed transfer
    """
    thread_list = []
    server_file = './server_list.txt'
    color = 0
    json_q = queue.Queue()
    with open(server_file) as fp:
        line = fp.readline()
        while line:
            threads = get_client_thread(line.strip(), color, request.args.get('TIME'), request.args.get('COUNT'), json_q)
            thread_list += threads
            color = (color + 1) % 256
            for thread in threads:
                thread.start()
            line = fp.readline()

    for thread in thread_list:
        thread.join()

    
    return jsonify({'transfer': list(json_q.queue)})

if __name__ == "__main__":
    """
    The application will listen on the port 4025 waiting for get request to start.
    The request needs 2 parameters: TIME and COUNT. Time will represent the interval of time that
    copycat needs to control (i.e. last 3 hours). Count will represent the number of times that 
    a file needs to have been request to justify the copy from serverA to serverB.
    """
    app.run(debug=True, host="0.0.0.0", port=4025)
