import threading, queue, traceback
from collections import Counter
from datetime import time
import time
from database import Database
import os, requests
from colored import fg, attr
import simplejson as json
r"""Thread which actually copy a file from a ftp server to another
This module handle the thread which will get the requests of the last 2
hours from the database, will count it and then will decide if is needed
to copy a certain file from the original server to the nearest. 

Constants
---------
DEFAULT_PSW: to keep the simulation as easy as possible each user has the same password
RESET: default attribute to reset console color

"""
DEFAULT_PSW = 'password' #os.environ['DEFAULT_USER']
DEFAULT_USER = 'username' #os.environ['DEFAULT_PSW']
MANAGER_IP = '192.168.1.188' #os.environ['MANAGER_IP']
MANAGER_PORT = '7025' #os.environ['MANAGER_IP']
RESET = attr('reset')

def count_element(result_set):
    """
        this method will count the number of times that every file has been requested. To do that it uses the object Counter from the collections library.
     """
    n_request = []
    for request in result_set:
        request = request['file_path'].split("/")
        n_request.append(request[len(request) - 1])
    n_request = Counter(n_request)
    return n_request.most_common()


class Mover(threading.Thread):
    """
    Represent the checker and copy-file handler of the system
    Attributes:
        -db: represent the database handler object
        -server: represent the server which is being checked
        -client: represent the client which is being checked
        -color: represent the unique color of the thread
    """
    def __init__(self, server, client, color, json_q, time="2h", count=3):
        super(Mover, self).__init__()
        self.db = Database()
        self.server = server
        self.client = client
        self.color = fg(str(color))
        self.count = count
        self.time = time
        self.json_q = json_q

    def run(self):
        """
        This is the core of the thread, this method will get the requests from the server,
        will count the number of times of each distinct file has been requested and than
        will decide if a copy is needed. If is needed than it will proceed by doing it.
        """
        try:
            result_set = self.db.select_all_time(self.time, self.server[2], self.client[0])
            result_set = result_set.get_points(measurement='request')
            n_request = count_element(result_set)
            print(self.color + "Checking client: " + str(self.client) + " On server: " + str(self.server) + RESET, flush=True)
            for filename, n in n_request:
                print(self.color + "File name: " + filename + " Count: " + str(n) + RESET, flush=True)
                if n >= int(self.count):
                    print(self.color + "Mooving file: " + filename + " from server: " + str(self.server) + RESET, flush=True)
                    start = time.time()
                    manager = 'http://' + MANAGER_IP + ':' + MANAGER_PORT + '?server_ip=' + self.client[1] + '&server_port=' + self.client[2] + '&filename=' + filename
                    check = requests.get(manager).json()
                    end = time.time()
                    if check['result']:
                        self.json_q.put({
                            'filename': filename,
                            'from_server': self.server[0],
                            'to_server': self.client[1],
                            'time': str(end - start)
                        })
                        print(self.color + "File: " + filename + " copied " + "in: " + str(end - start) + " sec" + RESET, flush=True)
                    else:
                        print(self.color + "An error occurred during the process of the copy of the file " + filename + RESET)
        except ConnectionError: 
            print(self.color + "ConnectionErrorException: maybe the Database or the FTP servers are down?" + RESET)
        except AttributeError:
            print(self.color + "AttributeErrorException: the database return none instead than a result set." + RESET)
        except Exception as ex:
            print(self.color + str(ex.__class__) + " "+ str(ex.__class__.__name__) + RESET)
            tb = traceback.format_exc()
            print(self.color + str(tb) + RESET)
            return False

    def __str__(self):
        return self.color + "CLIENT: " + str(self.client) + "\nSERVER: " + str(self.server) + RESET
