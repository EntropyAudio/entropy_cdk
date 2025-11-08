from aws_cdk import Environment, App
from src.stack.apig_stack import APIGStack, APIGStackProps
from src.stack.ddb_stack import DDBStack
from src.stack.s3_stack import S3Stack
from src.stack.lambda_stack import LambdaStack, LambdaStackProps

app = App()
env = Environment(account="533267269362", region="us-east-1")

s3_stack = S3Stack(
    scope=app,
    construct_id="EntropyAudioS3Stack",
    env=env,
)

ddb_stack = DDBStack(
    scope=app,
    construct_id="EntropyAudioDDBStack",
    env=env,
)

lambda_stack = LambdaStack(
    scope=app,
    construct_id="EntropyAudioLambdaStack",
    env=env,
    props=LambdaStackProps(
        s3_stack=s3_stack,
        ddb_stack=ddb_stack,
    )
)

apig_stack = APIGStack(
    scope=app,
    construct_id="EntropyAudioAPIStack",
    env=env,
    props=APIGStackProps(
        lambda_stack=lambda_stack
    )
)

app.synth()
