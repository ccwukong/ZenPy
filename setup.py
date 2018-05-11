from setuptools import setup, find_packages

setup(
    name='zen-py',
    keywords=['serverless', 'automation', 'aws'],
    description='A set of AWS service automation tools',
    license='Apache License 2.0',
    install_requires=['boto3', 'pymysql', 'requests', "click"],
    version='0.0.0.19',
    entry_points={
          'console_scripts': [
              'zen = zenpy.zen:master_command'
          ]
      },
    author='Chen Cheng',
    author_email='ccwukong@gmail.com',
    packages=find_packages(),
    platforms='any',
)
