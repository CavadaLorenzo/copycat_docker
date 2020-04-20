from influxdb import InfluxDBClient
import requests, os

DB_IP = '192.168.1.188' #os.environ['DB_IP']
DB_PORT = '8089' #os.environ['DB_PORT']
DB_NAME = 'db0' #os.environ['DB_NAME']


class Database:
    r"""This class will handle the connection to the IfluxDB database.
    By default it connects to localhost throw the port 8086.
    This can be changed when the object Database is created specifying
    the host IP, the port and the name of the database.

    """

    def __init__(self):
        self.db = InfluxDBClient(DB_IP, DB_PORT)
        self.db.switch_database(DB_NAME)

    def select_all_time(self, time, logviewer_id, username):
        """
        This method will get the request from a InfluxDB database of the last
        hours (TIME CONSTANT) made by a specific client to a specific server.
        It will return a result_set with all the received entry
        """
        try:
            query = "SELECT * FROM request WHERE time \u003e now() - " + time + " AND logviewer_id = '" + logviewer_id + "' AND username = '" + username + "'"
            result = self.db.query(query)
            return result
        except requests.exceptions.ConnectionError:
            print("ConnectionError exception, maybe the database is down?")
