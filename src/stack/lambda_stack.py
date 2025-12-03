from aws_cdk import Stack, Duration
from aws_cdk import aws_logs
from aws_cdk.aws_lambda import Function as Lambda, Runtime, Code, Architecture
from aws_cdk.aws_s3 import Bucket
from aws_cdk.aws_secretsmanager import Secret
from aws_cdk.aws_dynamodb import Table
from constructs import Construct
from pathlib import Path
from ..utils import constants as c


class LambdaStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        lambda_zip_path = Path(__file__).resolve().parents[3] / "entropy_lambda" / "Lambda.zip"

        audio_data_bucket = Bucket.from_bucket_name(
            self,
            id=f"{c.AUDIO_DATA_BUCKET}_ID",
            bucket_name=c.AUDIO_DATA_BUCKET,
        )

        audio_metadata_table = Table.from_table_name(
            self,
            id=f"{c.AUDIO_METADATA_TABLE_NAME}_ID",
            table_name=c.AUDIO_METADATA_TABLE_NAME
        )

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
        audio_data_bucket.grant_read_write(self.audio_generation_controller_lambda)
        audio_metadata_table.grant_read_write_data(self.audio_generation_controller_lambda)

        self.audio_generation_controller_lambda.add_environment(c.ENV_AUDIO_DATA_BUCKET, audio_data_bucket.bucket_name)
        self.audio_generation_controller_lambda.add_environment(c.ENV_AUDIO_METADATA_TABLE, audio_metadata_table.table_name)

        self.audio_selection_lambda = Lambda(
            self,
            id="AudioSelection",
            function_name="AudioSelection",
            runtime=Runtime.PYTHON_3_13,
            handler="src.handler.audio_selection_handler.lambda_handler",
            code=Code.from_asset(str(lambda_zip_path)),
            architecture=Architecture.ARM_64,
            timeout=Duration.seconds(5),
            memory_size=128,
            log_retention=aws_logs.RetentionDays.ONE_WEEK
        )

        audio_metadata_table.grant_read_write_data(self.audio_selection_lambda)

        self.audio_selection_lambda.add_environment(c.ENV_AUDIO_DATA_BUCKET, audio_data_bucket.bucket_name)
        self.audio_selection_lambda.add_environment(c.ENV_AUDIO_METADATA_TABLE, audio_metadata_table.table_name)