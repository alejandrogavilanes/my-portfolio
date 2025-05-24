# Import specific classes from boto3 and botocore
from boto3.resources.base import ServiceResource
from boto3.s3.bucket import Bucket
from botocore.client import Config
from zipfile import ZipFile  # Import ZipFile class from zipfile module
import logging  # import logging for error handling

# Initialize S3 resource with specific configuration
s3: ServiceResource = ServiceResource('s3', config=Config(signature_version='s3v4'))

build_bucket: Bucket = s3.Bucket('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
portfolio_bucket: Bucket = s3.Bucket('XXXXXXXXXXXXXXXXXXXXXXXXXXX')

# On Windows, this will need to be a different location than /tmp
try:
    build_bucket.download_file('portfolio.zip', '/tmp/portfolio.zip')

    with ZipFile('/tmp/portfolio.zip') as myzip:
        for nm in myzip.namelist():
            try:
                obj = myzip.open(nm)
                portfolio_bucket.upload_fileobj(obj, nm)
                portfolio_bucket.Object(nm).Acl().put(ACL='public-read')
            except Exception as e:
                logging.error(f"Error processing file {nm}: {str(e)}")
except Exception as e:
    logging.error(f"Error downloading or processing zip file: {str(e)}")
