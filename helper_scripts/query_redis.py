# -*- coding: utf-8 -*-

import boto3
import datetime
import redis
import redis_stack_configs

REDIS_HOST = redis_stack_configs.REDIS_HOST
REDIS_PORT = redis_stack_configs.REDIS_PORT
BUCKET_NAME = redis_stack_configs.BUCKET_NAME

r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)

# Query S3 Data
s3 = boto3.resource('s3')

keys = []
i = 0

while i < 100:

    # Start timer
    start = datetime.datetime.now()

    value = r.get(BUCKET_NAME + ':filename' + str(i) + '.txt')

    end = datetime.datetime.now()
    # End timer

    delta = end - start
    millis = delta.seconds * 1000000
    millis += delta.microseconds
    keys.append(millis)
    i += 1

while i < 100:
    # PUT data in S3
    object = s3.Object(BUCKET_NAME, 'filename' + str(i) + '.txt')
    object.put(Body="This is some generated data for filename" + str(i) + '.txt')
    # Cache the data [ KEY = bucket:filenameX.txt]
    r.set(BUCKET_NAME + ':filename' + str(i) + '.txt',
          'This is some generated data for filename' + str(i) + '.txt')
    i += 1

# throw out first request due to initialization overhead
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
