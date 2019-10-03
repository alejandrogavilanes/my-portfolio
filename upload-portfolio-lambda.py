import boto3
from botocore.client import Config
import StringIO
import zipfile
import mimetypes
s3 = boto3.resource('s3', config=Config(signature_version='s3v4'))

# set s3 target bucket
portfolio_bucket = s3.Bucket('portfolio-alex-project')
# set codebuild bucket used to stage zip pulled from GIT hub
build_bucket = s3.Bucket('alexbuild.port')

#use StringIO to pull zip file in memory
portfolio_zip = StringIO.StringIO()
build_bucket.download_fileobj('alexbuild.port.zip', portfolio_zip)

#unzip file, load to target bucket and set file type using mimetypes
# last but sets permissions on S3 ACL to public for all files
with zipfile.ZipFile(portfolio_zip) as myzip:
    for rm in myzip.namelist():
        obj = myzip.open(rm)
        portfolio_bucket.upload_fileobj(obj, rm,
            ExtraArgs={'ContentType': mimetypes.guess_type(rm)[0]})
        portfolio_bucket.Object(rm).Acl().put(ACL='public-read')
