import boto3
import logging
import json
import datetime

s3_client = boto3.client('s3')
BUCKET_NAME = "jucygan-otodom-raw-data-bronze"

cloud_data = s3_client.list_objects_v2(Bucket=BUCKET_NAME)
threshold_date = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=7)

logging.info(f"Treshold date:{threshold_date}")

for ad in cloud_data.get('Contents', []):
    key = ad['Key']
    last_modified = ad['LastModified']

    if last_modified <= threshold_date:
        s3_client.delete_object(Bucket=BUCKET_NAME, Key=key)
        logging.info(f"Deleted {key} add from AWS S3")