#!/usr/bin/env python3

from aws_cdk import core

from elasticache_for_app_performance.elasticache_for_app_performance_stack import ElasticacheForAppPerformanceStack


app = core.App()
ElasticacheForAppPerformanceStack(app, "elasticache-for-app-performance")

app.synth()
