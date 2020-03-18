# -*- coding: utf-8 -*-

import logging as log
import os
import random
import string
import uuid

import boto3
import cfnresponse
import redis


def random_str_generator(size=40, chars=string.ascii_uppercase + string.digits):
    ''' Generate Random String for given string length '''
    return ''.join(random.choice(chars) for _ in range(size))


def lambda_handler(event, context):
    log.getLogger().setLevel(log.INFO)

    # This needs to change if there are to be multiple resources in the same stack
    physical_id = 'TheOnlyCustomResource'

    try:
        log.info(f'Input event: {event}')

        # Check if this is a Create and we're failing Creates
        if event['RequestType'] == 'Create' and event['ResourceProperties'].get('FailCreate', False):
            raise RuntimeError('Create failure requested')

        # Do the thing
        # OriginalCode
        message = event['ResourceProperties']['Message']

        # MINE
        REDIS_HOST = os.environ.get('REDIS_HOST')
        REDIS_PORT = os.environ.get('REDIS_PORT')
        BUCKET_NAME = os.environ.get('BUCKET_NAME', 6379)
        RECORD_COUNT = os.environ.get('RECORD_COUNT', 200)

        if not REDIS_HOST or not BUCKET_NAME:
            log.info(
                f'Either REDIS_HOST:{REDIS_HOST} or BUCKET_NAME:{BUCKET_NAME} is none')
            return cfnresponse.send(event, context, cfnresponse.FAILED, {}, physical_id)

        r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
        log.info(f'All Went fine')
        # Load data into S3 & Redis
        s3 = boto3.resource('s3')
        i = 0
        while i < int(RECORD_COUNT):
            # Generate Random String for file content
            random_str = random_str_generator(random.randrange(200, 400))
            random_txt = f'Mystique Automation Powers Valaxy. {random_str}'
            # PUT data in S3
            object = s3.Object(BUCKET_NAME, 'filename' + str(i) + '.txt')
            object.put(Body=random_txt)
            # Cache the data [ KEY = bucket:filenameX.txt]
            r.set(BUCKET_NAME + ':filename' + str(i) + '.txt', random_txt)
            i += 1
        print("Data loaded successfully!")
        # MINE

        attributes = {
            'Response': f"Message sent from function. MessageReceived:{message}"
        }

        cfnresponse.send(event, context, cfnresponse.SUCCESS,
                         attributes, physical_id)
    except Exception as e:
        log.exception(e)
        # cfnresponse's error message is always "see CloudWatch"
        cfnresponse.send(event, context, cfnresponse.FAILED, {}, physical_id)
