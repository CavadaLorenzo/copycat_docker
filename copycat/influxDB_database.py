from influxdb import InfluxDBClient
import requests, os


try:    DB_IP = os.environ['DB_IP']
except:    DB_IP = '192.168.1.188' 
try:    DB_PORT = os.environ['DB_PORT']
except:    DB_PORT = '8089' 
try:    DB_NAME = os.environ['DB_NAME']
except:    DB_NAME = 'db0' 

class InfluxDB_DB:
    r"""This class will handle the connection to the IfluxDB database.
    By default it connects to localhost throw the port 8086.
    This can be changed when the object Database is created specifying
    the host IP, the port and the name of the database.

    """

    def __init__(self):
        self.db = InfluxDBClient(DB_IP, DB_PORT)
        self.db.switch_database(DB_NAME)

    def select_all_time(self, time, server_id):
        """
        This method will get the request from a InfluxDB database of the last
        hours (time param) made to a specific server.
        It will return a result_set with all the received entry
        """
        try:
            request_list = []
            query = "SELECT * FROM request WHERE time \u003e now() - " + time + " AND logviewer_id = '" + server_id + "'"
            print(query)
            result_set = self.db.query(query).get_points(measurement='request')            
            for request in result_set:
                request_list.append(request)

            return request_list
        except requests.exceptions.ConnectionError:
            print("ConnectionError exception, maybe the database is down?")