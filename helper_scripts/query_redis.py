# -*- coding: utf-8 -*-

import boto3
import datetime
import redis
import random
import constants

REDIS_HOST = constants.REDIS_HOST
REDIS_PORT = constants.REDIS_PORT
BUCKET_NAME = constants.BUCKET_NAME
RECORD_COUNT = constants.RECORD_COUNT

# Create connection to Redis
r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)

keys = []
i = 0


while i < int(RECORD_COUNT):
    # Randomize file seek
    _seeker = random.randrange(1, 199)

    # Start timer
    start = datetime.datetime.now()

    value = r.get(BUCKET_NAME + ':filename' + str(_seeker) + '.txt')

    end = datetime.datetime.now()
    # End timer

    delta = end - start
    millis = delta.seconds * 1000000
    millis += delta.microseconds
    keys.append(millis)
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
