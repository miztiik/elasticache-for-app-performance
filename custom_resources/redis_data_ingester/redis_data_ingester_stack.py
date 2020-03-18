from aws_cdk import aws_cloudformation as cfn
from aws_cdk import aws_iam as _iam
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_ec2 as _ec2
from aws_cdk import core


class redis_data_ingester(core.Construct):
    def __init__(self, scope: core.Construct, id: str, config_params, ** kwargs) -> None:
        super().__init__(scope, id)

        # Lambda Layer for Redis
        redis_lib_layer = _lambda.LayerVersion(self, "redisPythonLibLayer",
                                               code=_lambda.Code.from_asset(
                                                   "custom_resources/redis_data_ingester/lambda_src/layer_code/redis_lib_python37.zip"),
                                               compatible_runtimes=[
                                                   _lambda.Runtime.PYTHON_3_7],
                                               license=f"This product uses redis code from https://pypi.org/project/redis/ library",
                                               description="Layer to connect to redis using python"
                                               )

        # Read LambdaFunction Code
        try:
            with open("custom_resources/redis_data_ingester/lambda_src/redis_data_ingester_lambda_function.py", encoding="utf-8") as fp:
                code_body = fp.read()
        except OSError:
            print('Unable to read UserData script')

        # Create IAM Permission Statements that are required by the Lambda

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

        roleStmt1 = _iam.PolicyStatement(
            effect=_iam.Effect.ALLOW,
            resources=['*'],
            actions=['ec2:CreateNetworkInterface',
                     'ec2:DescribeNetworkInterfaces',
                     'ec2:DeleteNetworkInterface']
        )
        roleStmt1.sid = "AllowLambdaToManageVPCENI"

        roleStmt2 = _iam.PolicyStatement(
            effect=_iam.Effect.ALLOW,
            resources=[
                f"{config_params.get('BUCKET').bucket_arn}/*"
            ],
            actions=['s3:GetObject',
                     's3:PutObject']
        )
        roleStmt2.sid = "AllowS3ObjectReadWriteAccess"

        redis_data_ingester_fn = _lambda.SingletonFunction(
            self, "Singleton",
            uuid="mystique30-4ee1-11e8-9c2d-fa7ae01bbebc",
            code=_lambda.InlineCode(code_body),
            handler="index.lambda_handler",
            timeout=core.Duration.seconds(300),
            runtime=_lambda.Runtime.PYTHON_3_7,
            environment={
                'LD_LIBRARY_PATH': '/opt/python',
                'REDIS_HOST': config_params.get('REDIS_HOST'),
                'REDIS_PORT': config_params.get('REDIS_PORT'),
                'BUCKET_NAME': config_params.get('BUCKET_NAME'),
                'RECORD_COUNT': config_params.get('RECORD_COUNT')
            },
            layers=[redis_lib_layer],
            security_group=config_params.get('REDIS_SG'),
            vpc=config_params.get('VPC'),
            vpc_subnets=_ec2.SubnetType.PRIVATE
        )

        redis_data_ingester_fn.add_to_role_policy(roleStmt1)
        redis_data_ingester_fn.add_to_role_policy(roleStmt2)

        resource = cfn.CustomResource(
            self, "Resource",
            provider=cfn.CustomResourceProvider.lambda_(
                redis_data_ingester_fn
            ),
            properties=kwargs,
        )

        self.response = resource.get_att("Response").to_string()
