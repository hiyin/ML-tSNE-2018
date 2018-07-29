import MySQLdb

def db_connect():
    # parameter for connection: (host, user, password, database)
    return MySQLdb.connect("localhost", "singleton", "singleton", "singleton")
