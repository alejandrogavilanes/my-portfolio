# Import specific classes from boto3 and botocore
from boto3.resources.base import ServiceResource
from botocore.client import Config
from io import BytesIO  # Import BytesIO from io module
from zipfile import ZipFile  # Import ZipFile from zipfile module

# Import specific boto3 services
from boto3 import client as boto3_client  # boto3 client for AWS services
from boto3 import resource as boto3_resource  # boto3 resource for AWS services

# Import necessary modules
import boto3
from botocore.config import Config
import zipfile
from tempfile import NamedTemporaryFile
import logging

def lambda_handler(event, context):
    return process_portfolio_deployment(event)

def process_portfolio_deployment(event):
    sns, topic = setup_sns()
    location = get_artifact_location(event)
    
    try:
        logging.info(f"Building portfolio from {location}")
        s3 = setup_s3()
        portfolio_bucket, build_bucket = setup_buckets(s3, location)
        
        deploy_portfolio(build_bucket, portfolio_bucket, location)
        
        publish_success(topic)
        update_pipeline_status(event)
    except Exception as e:
        handle_error(topic, e)
    
    return 'Hello from Lambda'

def setup_sns():
    sns = boto3.resource('sns')
    topic = sns.Topic('arn:aws:sns:eu-west-2:147138840524:deployPortfolioTopic')
    return sns, topic

def get_artifact_location(event):
    job = event.get("CodePipeline.job")
    if job:
        for artifact in job["data"]["inputArtifacts"]:
            if artifact["name"] == "portfolioPipeline":
                return artifact["location"]["s3Location"]
    return {
        "bucketName": 'XXXXXXXXXXXXXX',
        "objectKey": 'testalexbuild.zip'
    }

def setup_s3():
    return boto3.resource('s3', config=Config(signature_version='s3v4'))

def setup_buckets(s3, location):
    portfolio_bucket = s3.Bucket('XXXXXXXXXXXXXXXXXXXXXX')
    build_bucket = s3.Bucket(location["XXXXXXXXXX"])
    return portfolio_bucket, build_bucket

def deploy_portfolio(build_bucket, portfolio_bucket, location):
    with NamedTemporaryFile() as temp_file:
        build_bucket.download_fileobj(location["objectKey"], temp_file)
        temp_file.seek(0)
        with zipfile.ZipFile(temp_file) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                portfolio_bucket.upload_fileobj(obj, nm)
                portfolio_bucket.Object(nm).Acl().put(ACL='public-read')

def publish_success(topic):
    topic.publish(Subject="Portfolio Deployed", Message="Portfolio Deployed Successfully.")

def update_pipeline_status(event):
    job = event.get("CodePipeline.job")
    if job:
        codepipeline = boto3.client('codepipeline')
        codepipeline.put_job_success_result(jobId=job["id"])

def handle_error(topic, error):
    topic.publish(Subject="Portfolio Deployment Failed", Message=f"The portfolio was not deployed successfully. Error: {str(error)}")
    raise
