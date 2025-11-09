from aws_cdk import Stack, RemovalPolicy
from aws_cdk.aws_s3 import Bucket, BucketEncryption, BlockPublicAccess, CorsRule, HttpMethods
from constructs import Construct


class S3Stack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        self.audio_data_bucket = Bucket(
            self,
            id="AudioData",
            bucket_name=f"entropy-audio-data-{self.region}",
            encryption=BucketEncryption.S3_MANAGED,
            block_public_access=BlockPublicAccess.BLOCK_ALL,
            enforce_ssl=True,
            versioned=True,
            removal_policy=RemovalPolicy.RETAIN,
            cors=[
                CorsRule(
                    allowed_methods=[HttpMethods.GET, HttpMethods.POST],
                    allowed_origins=["http://localhost:4200", "https://entropyaudio.io"],
                    allowed_headers=["*"]
                )
            ]
        )
