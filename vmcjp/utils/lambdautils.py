import json
import boto3

from botocore.session import Session
from botocore.config import Config

def call_lambda(function, data):
    s = Session()
    clientLambda = s.create_client(
        "lambda", 
        config=Config(retries={'max_attempts': 0})
    )
    clientLambda.invoke(
        FunctionName=function,
        InvocationType="Event",
        Payload=json.dumps(data)
    )

def call_lambda_async(function, data):
    s = Session()
    clientLambda = s.create_client(
        "lambda", 
        config=Config(retries={'max_attempts': 0})
    )
    clientLambda.invoke(
        FunctionName=function,
        InvocationType="Event",
        Payload=json.dumps(data)
    )

def call_lambda_sync(function, data):
#    s = Session()
#    clientLambda = s.create_client(
#        "lambda", 
#        config=Config(retries={'max_attempts': 0})
#    )
    lambda = boto3.client('lambda')
    response = client.invoke(
        FunctionName=function,
        InvocationType="RequestResponse",
        Payload=json.dumps(data)
    )
#    response = clientLambda.invoke(
#        FunctionName=function,
#        InvocationType="RequestResponse",
#        Payload=json.dumps(data)
#    )
    body = json.loads(response['Payload'].read())
    return body
