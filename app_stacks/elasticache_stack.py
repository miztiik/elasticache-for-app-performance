from aws_cdk import aws_ec2 as _ec2
from aws_cdk import aws_elasticache as _elasticache
from aws_cdk import aws_iam as _iam
from aws_cdk import aws_s3 as _s3
from aws_cdk import core

from custom_resources.redis_data_ingester.redis_data_ingester_stack import redis_data_ingester


class global_args:
    '''
    Helper to define global statics
    '''
    OWNER = "MystiqueInfoSecurity"
    ENVIRONMENT = "production"
    REPO_NAME = 'elasticache-for-app-performance'
    SOURCE_INFO = f'https://github.com/miztiik/{REPO_NAME}'


class ElasticacheForAppPerformanceStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, vpc, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Read BootStrap Script
        try:
            with open("bootstrap_scripts/install_httpd.sh", mode="r") as file:
                user_data = file.read()
        except OSError:
            print('Unable to read UserData script')

        # Get the latest AMI from AWS SSM
        linux_ami = _ec2.AmazonLinuxImage(generation=_ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
                                          edition=_ec2.AmazonLinuxEdition.STANDARD,
                                          virtualization=_ec2.AmazonLinuxVirt.HVM,
                                          storage=_ec2.AmazonLinuxStorage.GENERAL_PURPOSE
                                          )

        # Read BootStrap Script
        try:
            with open("bootstrap_scripts/install_httpd.sh", mode="r") as file:
                user_data = file.read()
        except OSError:
            print('Unable to read UserData script')

        # Get the latest ami
        amzn_linux_ami = _ec2.MachineImage.latest_amazon_linux(
            generation=_ec2.AmazonLinuxGeneration.AMAZON_LINUX_2
        )
        # ec2 Instance Role
        _instance_role = _iam.Role(self, "webAppClientRoleId",
                                   assumed_by=_iam.ServicePrincipal(
                                       'ec2.amazonaws.com'),
                                   managed_policies=[
                                       _iam.ManagedPolicy.from_aws_managed_policy_name(
                                           'AmazonSSMManagedInstanceCore'
                                       ),
                                       _iam.ManagedPolicy.from_aws_managed_policy_name(
                                           'AmazonS3ReadOnlyAccess'
                                       )
                                   ])
        # web_app_client Instance
        web_app_client = _ec2.Instance(self,
                                       "webAppClient",
                                       instance_type=_ec2.InstanceType(
                                           instance_type_identifier="t2.micro"),
                                       instance_name="web_app_Client",
                                       machine_image=amzn_linux_ami,
                                       vpc=vpc,
                                       vpc_subnets=_ec2.SubnetSelection(
                                           subnet_type=_ec2.SubnetType.PUBLIC
                                       ),
                                       role=_instance_role,
                                       user_data=_ec2.UserData.custom(
                                           user_data)
                                       )

        # S3 Bucket
        app_data_bkt = _s3.Bucket(self, "appDataBkt",
                                  removal_policy=core.RemovalPolicy.DESTROY)

        output_0 = core.CfnOutput(self,
                                  "SecuirtyAutomationFrom",
                                  value=f"{global_args.SOURCE_INFO}",
                                  description="To know more about this automation stack, check out our github page."
                                  )

        output_1 = core.CfnOutput(self,
                                  "ApplicationClient",
                                  value=web_app_client.instance_id,
                                  description=f"The instance to be used as app client for testing performance"
                                  )
        output_2 = core.CfnOutput(self,
                                  "MonitoredS3Bucket",
                                  value=(
                                      f"https://console.aws.amazon.com/s3/buckets/"
                                      f"{app_data_bkt.bucket_name}"
                                  ),
                                  description=f"S3 Bucket to host application data"
                                  )

        # Security Group for redis
        redis_sg = _ec2.SecurityGroup(self, 'redisSecurityGroup',
                                      vpc=vpc,
                                      security_group_name='RedisSG',
                                      description="Security Group for Redis Cache",
                                      allow_all_outbound=True
                                      )

        # Allows Cache Cluster to receive traffic from application
        redis_sg.add_ingress_rule(_ec2.Peer.any_ipv4(),
                                  #   _ec2.Port.all_tcp(),
                                  _ec2.Port.tcp(6379),
                                  description="Allow Clients to fetch data from Redis Cache Cluster"
                                  )

        # Iterate the private subnets
        pvt_subnets = vpc.select_subnets(
            subnet_type=_ec2.SubnetType.PRIVATE
        )

        # Create the Redis Subnet Group
        redis_subnet_group = _elasticache.CfnSubnetGroup(self, 'redis-sg',
                                                         subnet_ids=pvt_subnets.subnet_ids,
                                                         description='subnet group for redis'
                                                         )

        # Apparently no CDK Construct(yet Mar2020) for ElastiCache. No love there
        # https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_elasticache/CfnCacheCluster.html
        # Lets use the CFn Construct
        redis_cluster = _elasticache.CfnCacheCluster(self, 'redisCluster',
                                                     cache_node_type='cache.t3.micro',
                                                     engine='redis',
                                                     num_cache_nodes=1,
                                                     port=6379,
                                                     cluster_name='miztiik-cluster',
                                                     cache_subnet_group_name=redis_subnet_group.ref,
                                                     vpc_security_group_ids=[
                                                         redis_sg.security_group_id],
                                                     auto_minor_version_upgrade=True

                                                     )
        redis_cluster.add_depends_on(redis_subnet_group)

        output_3 = core.CfnOutput(self, 'redisSg',
                                  value=redis_sg.security_group_id,
                                  export_name='redisSg',
                                  description='The ElastiCache Cluster Security Group Id'
                                  )
        output_4 = core.CfnOutput(self, 'redisClusterEndpoint',
                                  value=redis_cluster.attr_redis_endpoint_address,
                                  description='The endpoint of the ElastiCache Cluster'
                                  )
        output_5 = core.CfnOutput(self, 'redisClusterPort',
                                  value=redis_cluster.attr_redis_endpoint_port,
                                  description='The port of the ElastiCache Cluster'
                                  )

        # Lets load some dummy data into the ES Cluster & S3 using a custom lambda custom_resource
        ingest_data_redis = redis_data_ingester(
            self, "ingestData",
            config_params={
                "REDIS_HOST": redis_cluster.attr_redis_endpoint_address,
                'REDIS_PORT': '6379',
                "BUCKET_NAME": app_data_bkt.bucket_name,
                'RECORD_COUNT': '200',
                'BUCKET': app_data_bkt,
                'VPC': vpc,
                'REDIS_SG': redis_sg
            },
            message=[
                {
                    "REDIS_HOST": redis_cluster.attr_redis_endpoint_address,
                    'REDIS_PORT': '6379',
                    "BUCKET_NAME": app_data_bkt.bucket_name,
                    'RECORD_COUNT': '200'
                }
            ]
        )

        # Publish the custom resource output
        output_6 = core.CfnOutput(
            self, "RedisDataIngesterResponse",
            description="Redis Data Ingester Response from Lambda",
            value=ingest_data_redis.response
        )
