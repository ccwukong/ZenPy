import boto3
import sys
import os
sys.path.append(os.path.abspath('../models'))
from sql_model import MySQLModel

def sql_to_nosql():
    mysql_model = MySQLModel(host='carpal-api.cluwsec6wqyi.ap-southeast-1.rds.amazonaws.com',
                             username='cpadm',
                             password='2U#u[}aB5sVX6<3_',
                             db='carpal', 
                             nosql_schema={})
    mysql_model.mapping('select * from users')

if __name__ == '__main__':  
    sql_to_nosql()