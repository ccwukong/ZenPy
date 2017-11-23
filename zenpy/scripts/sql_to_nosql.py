import boto3
import sys
import os
current_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_path + '/../')
from models.sql_model import MySQLModel

def mysql_to_dynamodb(sql, nosql_schema):
    mysql_model = MySQLModel(host='carpal-api.cluwsec6wqyi.ap-southeast-1.rds.amazonaws.com',
                             username='cpadm',
                             password='2U#u[}aB5sVX6<3_',
                             db='carpal', 
                             nosql_schema=nosql_schema)

    gen = mysql_model.mapping(sql)

    for item in gen:
        print(item)

if __name__ == '__main__':
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