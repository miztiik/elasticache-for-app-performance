#!/usr/bin/env python3

from aws_cdk import core


from app_stacks.vpc_stack import VpcStack
from app_stacks.elasticache_stack import ElasticacheForAppPerformanceStack


app = core.App()

# VPC Stack for hosting EC2 and ElastiCache
vpc_stack = VpcStack(app, "elasticache-for-app-performance-vpc-stack")

# ElastiCache
ec2_stack = ElasticacheForAppPerformanceStack(
    app, "elasticache-for-app-performance", vpc=vpc_stack.vpc)


# Stack Level Tagging
core.Tag.add(app, key="Owner",
             value=app.node.try_get_context('owner'))
core.Tag.add(app, key="OwnerProfile",
             value=app.node.try_get_context('github_profile'))
core.Tag.add(app, key="GithubRepo",
             value=app.node.try_get_context('github_repo_url'))
core.Tag.add(app, key="ToKnowMore",
             value=app.node.try_get_context('youtube_profile'))


app.synth()
