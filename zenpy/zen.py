import click
import subprocess
from .scripts.lambdas import lambda_automate
from .scripts.sql_to_nosql import mysql_to_dynamodb


@click.command()
@click.option('--file', prompt='Provide the path of package.json file.')
@click.option('--json',
              prompt='Provide the lambda function ' +
                     'configuration in JSON format.')
def master_command(file='', json=''):
    lambda_automate(file, json)
    # mysql_to_dynamodb(file)

if __name__ == '__main__':
    master_command()
