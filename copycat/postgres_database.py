import psycopg2, os


# default value is used when KeyError exception is raised
try:    POSTGRES_IP =  os.environ['POSTGRES_IP'] 
except:    POSTGRES_IP = '192.168.1.188'
try:    POSTGRES_PORT = os.environ['POSTGRES_PORT'] 
except:    POSTGRES_PORT = '54320'
try:    POSTGRES_USER = os.environ['POSTGRES_USER'] 
except:    POSTGRES_USER = 'admin'
try:    POSTGRES_DB_NAME = os.environ['POSTGRES_DB_NAME'] 
except:    POSTGRES_DB_NAME = 'servers'
try:    POSTGRES_PASSWORD = os.environ['POSTGRES_PASSWORD'] 
except:    POSTGRES_PASSWORD = 'admin'

class Postgres_DB:
    def __init__(self):
        """
        Create an object PostgreDB which connect to the given database. 
        :param host: is the database IP
        :param database: is the name of the database
        :param user: is the user used to connect to the database
        :param password: is the password used to connect to the database
        :param port: is the port used to connecto to the database
        """
        self.conn = psycopg2.connect(host = POSTGRES_IP, 
                                    database = POSTGRES_DB_NAME, 
                                    user = POSTGRES_USER, 
                                    password = POSTGRES_PASSWORD,
                                    port = POSTGRES_PORT) 

    def get_servers_list(self):
        """
        This method will return a list of all the servers in the database
        """

        select_all_query = f"SELECT * FROM \"Servers\""
        cursor = self.conn.cursor()
        cursor.execute(select_all_query)
        server_list = []
        for server in cursor.fetchall():
            server_list.append({
                "server_id": server[0],
                "server_name": server[1],
                "server_ip": server[2],
                "server_port": server[3],
                "server_ssh_port": server[4]
            })
        
        return server_list