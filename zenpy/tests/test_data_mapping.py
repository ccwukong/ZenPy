import sys
import os
current_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_path + '/../')
from scripts.sql_to_nosql import mysql_to_dynamodb
import unittest

class TestDataMapping(unittest.TestCase):
    def test_mysql_to_dynamodb(self):
        self.assertEqual(True, False)
