import json
import boto3
import logging

from botocore.config import Config

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def call_lambda_async(function, data):
    config = Config(retries={'max_attempts': 0})
    client = boto3.client("lambda", config=config)
    
    client.invoke(
        FunctionName=function,
        InvocationType="Event",
        Payload=json.dumps(data)
    )

def call_lambda_sync(function, data):
    client = boto3.client("lambda")
    
    response = client.invoke(
        FunctionName=function,
        InvocationType="RequestResponse",
        Payload=json.dumps(data)
    )
    logging.info(response)
    body = json.loads(response['Payload'].read())
    logging.info(body)
    logging.info("!!! isntance {}".format(isinstance(body, dict)))
    if isinstance(body, dict) and body.get("errorMessage") is not None:
        raise Exception(body.get("errorMessage"))
    else:
        return body
