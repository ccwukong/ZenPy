import boto3
from boto3 import resource
from boto3.dynamodb.conditions import Key
import sys
import os
current_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_path + '/../')
import json
from models.sql_model import MySQLModel
from models.dynamodb import DynamoDB

def mysql_to_dynamodb(file):
    file = os.path.abspath(os.path.expanduser(file))
    try:
        with open(file) as data_file:
            data = json.load(data_file)
    except Exception as e:
        print('Error. Unable to load the setting file.')
        sys.exit()

    dynamo = DynamoDB('customer_orders')

    for item in data.get('mappings'):
        mysql_model = MySQLModel(host=item.get('sourceHost'),
                                 username=item.get('sourceUsername'),
                                 password=item.get('sourcePassword'),
                                 db=item.get('sourceDB'), 
                                 nosql_schema=item.get('targetSchema'))

        gen = mysql_model.mapping(item.get('sourceSQL'))

        for sub_item in gen:
            dynamo.add(sub_item)

if __name__ == '__main__':
    mysql_to_dynamodb('~/Downloads/package.json')