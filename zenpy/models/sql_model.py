import json
import pymysql

class SQLModel:
    def __init__(self, host, username, password, db, nosql_schema, size):
        raise NotImplementedError

    def mapping(self):
        raise NotImplementedError

class MySQLModel(SQLModel):
    def __init__(self, host, username, password, db, nosql_schema, size=500):
        self._nosql_schema = nosql_schema
        self._size = size
        self._host = host
        self._username = username
        self._password = password
        self._db = db

    def mapping(self, sql):
        try:
            connection = pymysql.connect(host=self._host,
                                         user=self._username,
                                         password=self._password,
                                         charset='utf8mb4',
                                         db=self._db,
                                         cursorclass=pymysql.cursors.DictCursor)

            with connection.cursor() as cursor:
                cursor.execute(sql)
                result = cursor.fetchall()
                print(result)
        finally:
            connection.close()

