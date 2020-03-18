# -*- coding: utf-8 -*-

import boto3
import datetime
import redis_stack_configs
import random

REDIS_HOST = redis_stack_configs.REDIS_HOST
REDIS_PORT = redis_stack_configs.REDIS_PORT
BUCKET_NAME = redis_stack_configs.BUCKET_NAME
RECORD_COUNT = redis_stack_configs.RECORD_COUNT

# Query & Record Individual GET requests on S3 Objects
s3 = boto3.resource('s3')

keys = []
i = 0

while i < int(RECORD_COUNT):
    # Randomize file seek
    _seeker = random.randrange(1, 201)

    # Start timer
    start = datetime.datetime.now()

    obj = s3.Object(BUCKET_NAME, 'filename' + str(_seeker) + '.txt')
    data = obj.get()['Body'].read().decode('utf-8')

    end = datetime.datetime.now()
# End timer

    # Parse each result into microseconds
    delta = end - start
    millis = delta.seconds * 1000000
    millis += delta.microseconds
    keys.append(millis)
    i += 1

# Throw out first request due to initialization overhead
keys.pop(0)

# print timing
sum = 0
for idx, timing in enumerate(keys):
    sum += timing
    # uncomment below to see timing for each request
    # print(f'Time of request:{idx} is {timing}')

print('=====Timing=====\n')

average = sum / len(keys)
print(f'Average Latency in Microseconds: {average}')
print(f'MAX Latency in Microseconds: {max(keys)}')
print(f'MIN Latency in Microseconds: {min(keys)}')
print(f'\nCompleted Successfully!')
