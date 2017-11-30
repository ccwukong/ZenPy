from decimal import *
import json
import pymysql
from .dynamodb import DynamoDB

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

            def map_row_to_schema(row, fields):
                return {k: DynamoDB.cast_value(v) for k, v in row.items() if k in fields}

            with connection.cursor() as cursor:
                cursor.execute(sql)
                result = cursor.fetchall()
                
                return (map_row_to_schema(item, self._nosql_schema.get('fields')) for item in result)
        finally:
            connection.close()

