import json
import os
import pymysql
from boto3 import resource
from boto3.dynamodb.conditions import Key
import numbers
import decimal

class DynamoDBModelMixin(object):  
    def __str__(self):
        return json.dumps(self.__dict__)

    def to_json(self):
        return json.dumps(self.__dict__)

    def to_dict(self):
        return self.__dict__

class DynamoDB(object):
    def __init__(self, table_name, allowed_type=None):
        self._dynamodb_resource = resource('dynamodb')
        self._table = self._dynamodb_resource.Table(table_name)
        self._allowed_type = allowed_type

    def add(self, item):
        if self._allowed_type:
            if isinstance(item, self._allowed_type):
                return self._table.put_item(Item=item)
            else:
                raise TypeError('Invalid argument. {} object is expected'.format(self._allowed_type))
        else:
            return self._table.put_item(Item=item)

    def add_batch(self, items):
        if isinstance(items, list):
            if self._allowed_type:
                new_list = list(filter(lambda item: isinstance(item, self._allowed_type), items))
                if len(items) != len(new_list):
                    raise TypeError('Invalid argument. {} object is expected for all list elements'.format(self._allowed_type))

            new_list = []
            for item in items:
                new_list.append({'PutRequest': {'Item':item}})

            if self._dynamodb_resource.batch_write_item(RequestItems={self._table.name: new_list}).get('UnprocessedItems'):
                raise RuntimeError('Unable to process the batch insertion process.')
            else:
                return True
        else:
            raise TypeError('Invalid argument. List object is expected')

    def get(self, key, value):
        return self._table.get_item(Key={key: value}).get('Item', None)

    def get_all(self, filter_key=None, filter_value=None, partial_match=False):
        """
        Perform a scan operation on table.
        Can specify filter_key (col name) and its value to be filtered.
        """

        if filter_key and filter_value:
            filtering_exp = Key(filter_key).eq(filter_value) if not partial_match else Key(filter_key).begins_with(filter_value)
            response = self._table.scan(FilterExpression=filtering_exp)
        else:
            response = self._table.scan()

        return response.get('Items', [])

    def update(self, key, value, update_key, update_value):
        # to prevent it from creating new item if key-value pair not found.
        # it should be handled by add function
        if self.get(key, value):
            return self._table.update_item(Key={key: value},
                                           UpdateExpression="SET {} = :updated".format(update_key),                   
                                           ExpressionAttributeValues={':updated': update_value},
                                           ReturnValues='UPDATED_NEW').get('Attributes', None)
        else:
            raise KeyError('No key-value pair found.')

    def delete(self, key, value):
        self._table.delete_item(Key={key: value})
        if self.get(key, value):
            raise KeyError('No key-value pair found and deleted')
        else:
            return True

    def purge(self):
        try:
            items = self._table.scan().get('Items', [])

            for item in items:
                self._table.delete_item(Key={list(item.keys())[0]: list(item.values())[0]})
        except Exception as e:
            raise e
    
    @staticmethod
    def cast_value(value):
        no_cast = (str, bool)
        if isinstance(value, numbers.Number):
            return decimal.Decimal(value)
        elif isinstance(value, no_cast):
            return value
         
