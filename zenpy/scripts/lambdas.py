import base64
import boto3
import json
import os
import sys
import shutil
import string
import time

def lambda_automate(file):
    try:
        # Load the list of lambda functions to be updated to AWS
        file = os.path.abspath(os.path.expanduser(file))
        try:
            with open(file) as data_file:
                data = json.load(data_file)
        except Exception as e:
            print('Error. Unable to load the setting file.')
            sys.exit()

        lambdas = data.get('lambdas', None)
        virtualenv = data.get('pythonVirtualenv')
        lambda_client = boto3.client('lambda',
                                    region_name=data.get('region'),
                                    aws_access_key_id=data.get('accessKey', ''),
                                    aws_secret_access_key=data.get('secretKey', ''))

        app_id = data.get('awsClientID')

        if not lambdas:
            print('ErrorNo lambbda functions found in setting file.')
            sys.exit()

        print('Start to package lambda functions...')

        cloudwatch_events = boto3.client('events')
        for item in lambdas:
            if not item.get('skip'):
                for stage in item.get('stages', []):
                    lambda_name = item.get('alias', '').split('.')[0] if item.get('alias', '') else item.get('name', '').split('.')[0] 
                    lambda_stage = '{}-{}'.format(lambda_name, stage)
                    path = item.get('path', '').rstrip('/')

                    if not os.path.isabs(path):
                        # in case relative path is given and not in format ~/file_path
                        path = os.path.abspath(os.path.expanduser(path))

                    path += '/' 

                    lambda_file_path = ''.join([path, item.get('name', '')])
                    
                    if not os.path.exists(lambda_file_path):
                        raise FileNotFoundError('Cannot find the lambda function {}'.format(item.get('name', '')))
                        sys.exit()

                    tmp_folder = ''.join([path, lambda_stage, '_']) + str(int(time.time()))

                    if not os.path.exists(tmp_folder):
                        os.makedirs(tmp_folder)

                    shutil.copy(lambda_file_path, tmp_folder)

                    #other file dependancies
                    for vendor_item in item.get('vendor', []):
                        for module in vendor_item.get('modules'):
                            tmp_module_folder = tmp_folder + '/' + module
                            
                            if not os.path.exists(tmp_module_folder):
                                os.makedirs(tmp_module_folder)

                            src_files = os.listdir(vendor_item.get('rootDirectory', '')+ '/' + module)
                            for f in src_files:
                                shutil.copy(vendor_item.get('rootDirectory', '') + '/' + module + '/' + f, 
                                            tmp_module_folder + '/' + f)

                    lambda_runtime = item.get('runtime', '')
                    if 'python' in lambda_runtime.lower():
                        os.system("source {}/bin/activate & pip install {} -t {}".format(
                            virtualenv.rstrip('/'),
                            ' '.join(item.get('packages')),
                            tmp_folder
                        ))
                    elif 'nodejs' in lambda_runtime.lower():
                        os.system("npm install --prefix {} {}".format(
                            tmp_folder, 
                            ' '.join(item.get('packages'))
                        ))

                    print('Packaging Lambda function {}...'.format(item.get('name', '')))

                    zip_file = shutil.make_archive(base_name=tmp_folder,
                                                   format='zip',
                                                   root_dir=tmp_folder, 
                                                   base_dir='./' )
                    shutil.rmtree(tmp_folder)

                    print('Done packaging lambda functions.')

                    print('Start to deploy lambda functions.')
                    with open(zip_file, 'rb') as f:
                        print('Deploying {}...'.format(lambda_stage))

                        try:
                            lambda_client.delete_function(FunctionName=lambda_stage)
                        except:
                            pass

                        #Let the script fail if anything goes wrong here
                        response = lambda_client.create_function(FunctionName=lambda_stage,
                                                                 Runtime=item.get('runtime', '').lower(),
                                                                 Role="arn:aws:iam::"+app_id+":role/"+item.get('iamRole', ''),
                                                                 Handler='.'.join([item.get('name', '').split('.')[0],
                                                                                   item.get('handler', '')]),
                                                                 Code={'ZipFile': f.read()},
                                                                 Environment={'Variables': item.get('environmentVariables')},
                                                                 Timeout=item.get('timeout', 3),
                                                                 Publish=True)

                        #Create cloudwatch event trigger for lambda function here
                        lambda_arn = response.get('FunctionArn', '')

                        events = item.get('events')
                        
                        for event in events:
                            #create rule here

                            if event.get('type') == 'CloudWatchEvent':
                                if event.get('schedule', None):
                                    response = cloudwatch_events.put_rule(Name=event.get('name'),
                                                                        RoleArn=event.get('iamRole'),
                                                                        ScheduleExpression=event.get('schedule'),
                                                                        State=event.get('state'))
                                else:
                                    response = cloudwatch_events.put_rule(Name=event.get('name'),
                                                                        RoleArn=event.get('iamRole'),
                                                                        State=event.get('state'))

                                response = lambda_client.add_permission(
                                    FunctionName=lambda_stage,
                                    StatementId=str(int(time.time())),
                                    Action='lambda:*',
                                    Principal='events.amazonaws.com',
                                    SourceArn=response.get('RuleArn')
                                )

                                response = cloudwatch_events.put_targets(Rule=event.get('name'),
                                                                        Targets=[
                                                                            {
                                                                                'Arn': lambda_arn,
                                                                                'Id': '{}CloudWatchEventsTarget'.format(lambda_stage),
                                                                            }
                                                                        ])
                            elif event.get('type') == 'SNS':
                                if event.get('stage') == stage:
                                    response = lambda_client.add_permission(
                                        FunctionName=lambda_stage,
                                        StatementId=str(int(time.time())),
                                        Action='lambda:*',
                                        Principal='sns.amazonaws.com',
                                        SourceArn=event.get('topicARN'))                            
                    
                print('Done deploying '+ item.get('name', ''))
        print('Success! Done deploying.')
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise e