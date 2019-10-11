import boto3
from botocore.client import Config
import StringIO
import zipfile

def lambda_handler(event, context):

    # Used to link to AWS sns to send message to a topic
    sns = boto3.resource('sns')
    topic = sns.Topic('arn:aws:sns:eu-west-2:147138840524:deployPortfolioTopic')

    # here we are setting object for code pipeline so it can create a S3 bucket with a non random name
    location = {
        "bucketName": 'alexbuild.port',
        "objectKey": 'testalexbuild.zip'
    }
        # try is used to catch error
    try:
        #this sets objcet job to codepipeline job
        job = event.get("CodePipeline.job")
        if job:
            #using a for loop to go over all elements of the copepipeline artefact looking for the passing to build_bucket function
            for artifact in job["data"]["inputArtifacts"]:
                if artifact["name"] == "portfolioPipeline":
                    location = artifact["location"]["s3Location"]

        # used to print out on logs
        print "Building portfolio from " + str(location)

        s3 = boto3.resource('s3', config=Config(signature_version='s3v4'))
        # set s3 target bucket
        portfolio_bucket = s3.Bucket('portfolio-alex-project')
        # set codebuild bucket used to stage zip pulled from GIT hub
        build_bucket = s3.Bucket(location["bucketName"])

        #use StringIO to pull zip file in memory
        portfolio_zip = StringIO.StringIO()
        build_bucket.download_fileobj(location["objectKey"], portfolio_zip)

        #unzip file, load to target bucket and set file type using mimetypes
        # last but sets permissions on S3 ACL to public for all files
        with zipfile.ZipFile(portfolio_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                portfolio_bucket.upload_fileobj(obj, nm)
                portfolio_bucket.Object(nm).Acl().put(ACL='public-read')

        print "Job done"
        topic.publish(Subject="Portofolio Deployed", Message="Portfolio Deployed Successfully.")
        # for codepipeline so that build was successfull
        if job:
            codepipeline = boto3.client('codepipeline')
            codepipeline.put_job_success_result(jobId=job["id"])

    #this ends the try and sends message to the sns Topic
    except:
        topic.publish(Subject="Portfolio Deployed Failed", Message="The portofolio was not deployed successfully")
        raise

    return 'Hello from Lambda'
