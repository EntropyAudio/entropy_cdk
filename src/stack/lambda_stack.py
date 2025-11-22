from aws_cdk import Stack, Duration
from aws_cdk import aws_logs
from aws_cdk.aws_lambda import Function as Lambda, Runtime, Code, Architecture
from aws_cdk.aws_secretsmanager import Secret
from .ddb_stack import DDBStack
from .s3_stack import S3Stack
from constructs import Construct
from pathlib import Path
from dataclasses import dataclass
from ..utils import constants as c


@dataclass
class LambdaStackProps:
    s3_stack: S3Stack
    ddb_stack: DDBStack


class LambdaStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, props: LambdaStackProps, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        lambda_zip_path = Path(__file__).resolve().parents[3] / "entropy_lambda" / "Lambda.zip"

        runpod_api_key_secret = Secret.from_secret_name_v2(
            self, id="RunPodApiKeySecret", secret_name="RunPodApiKey"
        )

        self.audio_generation_controller_lambda = Lambda(
            self,
            id="AudioGenerationController",
            function_name="AudioGenerationController",
            runtime=Runtime.PYTHON_3_13,
            handler="src.handler.audio_generation_handler.lambda_handler",
            code=Code.from_asset(str(lambda_zip_path)),
            environment={
                c.ENV_RUNPOD_API_KEY_SECRET: runpod_api_key_secret.secret_name,
            },
            architecture=Architecture.ARM_64,
            timeout=Duration.seconds(30),
            memory_size=128,
            log_retention=aws_logs.RetentionDays.ONE_WEEK
        )

        runpod_api_key_secret.grant_read(self.audio_generation_controller_lambda)
        props.s3_stack.audio_data_bucket.grant_read_write(self.audio_generation_controller_lambda)
        props.ddb_stack.audio_metadata_table.grant_read_write_data(self.audio_generation_controller_lambda)

        self.audio_generation_controller_lambda.add_environment(c.ENV_AUDIO_DATA_BUCKET, props.s3_stack.audio_data_bucket.bucket_name)
        self.audio_generation_controller_lambda.add_environment(c.ENV_AUDIO_METADATA_TABLE, props.ddb_stack.audio_metadata_table.table_name)
