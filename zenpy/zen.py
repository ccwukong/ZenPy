import click
import subprocess
from .scripts.lambdas import lambda_automate
from .scripts.sql_to_nosql import mysql_to_dynamodb

@click.command()
@click.option('--mapping', default=1, help='Number of greetings.', prompt='m2d: Map MySQL to DynamoDB')
@click.option('--file', prompt='Provide the path of package.json file')
def master_command(mapping='', file=''):
    if file:
        lambda_automate(file)
    elif mapping:
        sql = '''select o.id as order_id, o.Orders_status_id as orders_status_id, os.status_name, od.driver_fee,  
                 o.Orders_types_Id as orders_types_id, ot.type_name, a.lat, a.long, a.google_place_id, 
                 o.Drivers_Id as drivers_id, u.first_name, u.last_name 
                 from orders as o
                 left join orders_details as od on o.Orders_details_Id=od.id
                 left join orders_types as ot on o.Orders_types_Id=ot.id
                 left join orders_status as os on o.Orders_status_id=os.id
                 left join _orders_addresses as _oa on o.id=_oa.Orders_id
                 left join addresses as a on _oa.Addresses_id=a.id and a.Address_types_Id=3
                 left join drivers as d on o.Drivers_Id = d.id
                 left join users as u on d.Users_Id=u.id'''

        mysql_to_dynamodb(sql, {'key': 'order_id', 
                                'sort_key':'status_name', 
                                'fields':{'order_id': 'Number',
                                          'orders_status_id': 'Number', 
                                          'status_name': 'String', 
                                          'driver_fee': 'Number', 
                                          'orders_types_id': 'Number', 
                                          'type_name': 'String', 
                                          'lat': 'Number', 
                                          'long': 'Number', 
                                          'google_place_id': 'String', 
                                          'drivers_id': 'Number', 
                                          'first_name': 'String', 
                                          'last_name': 'String'}})

if __name__ == '__main__':
    master_command()