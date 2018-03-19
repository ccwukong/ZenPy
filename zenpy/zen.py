import click
import subprocess
from .scripts.lambdas import lambda_automate
from .scripts.sql_to_nosql import mysql_to_dynamodb

@click.command()
@click.option('--file', prompt='Provide the path of package.json file')
def master_command(file='~/Downloads/package.json'):
    lambda_automate(file)
    #mysql_to_dynamodb(file)

if __name__ == '__main__':
    master_command()
