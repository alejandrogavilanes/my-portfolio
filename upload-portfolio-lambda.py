import boto3
from botocore.client import Config
import StringIO
import zipfile

def lambda_handler(event, context):
    s3 = boto3.resource('s3', config=Config(signature_version='s3v4'))
    # set s3 target bucket
    portfolio_bucket = s3.Bucket('portfolio-alex-project')
    # set codebuild bucket used to stage zip pulled from GIT hub
    build_bucket = s3.Bucket('alexbuild.port')

    #use StringIO to pull zip file in memory
    portfolio_zip = StringIO.StringIO()
    build_bucket.download_fileobj('testalexbuild.zip', portfolio_zip)

    #unzip file, load to target bucket and set file type using mimetypes
    # last but sets permissions on S3 ACL to public for all files
    with zipfile.ZipFile(portfolio_zip) as myzip:
        for nm in myzip.namelist():
            obj = myzip.open(nm)
            portfolio_bucket.upload_fileobj(obj, nm)
            portfolio_bucket.Object(nm).Acl().put(ACL='public-read')

    print "Job done!"

    return 'Hello from Lambda'
