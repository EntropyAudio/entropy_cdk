from aws_cdk import Stack, CfnOutput, Duration
from constructs import Construct
from dataclasses import dataclass

from .cognito_stack import CognitoStack
from .lambda_stack import LambdaStack
from aws_cdk.aws_apigatewayv2 import HttpApi, CorsPreflightOptions, CorsHttpMethod, HttpMethod
from aws_cdk.aws_apigatewayv2_integrations import HttpLambdaIntegration
from aws_cdk.aws_apigatewayv2_authorizers import HttpUserPoolAuthorizer

@dataclass
class APIGStackProps:
    lambda_stack: LambdaStack
    cognito_stack: CognitoStack


class APIGStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, props: APIGStackProps, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        authorizer = HttpUserPoolAuthorizer(
            "EntropyAudioAuthorizer",
            pool=props.cognito_stack.user_pool,
            user_pool_clients=[props.cognito_stack.user_pool_client]
        )

        audio_generation_controller_integration = HttpLambdaIntegration(
            "AudioGenerationControllerIntegration",
            handler=props.lambda_stack.audio_generation_controller_lambda
        )

        http_api = HttpApi(
            self,
            id="AudioGenerationService",
            api_name="AudioGenerationService",
            cors_preflight=CorsPreflightOptions(
                allow_origins=["*"],
                allow_methods=[CorsHttpMethod.GET, CorsHttpMethod.POST],
                max_age=Duration.days(10),
                allow_headers=["Authorization", "Content-Type"]
            )
        )

        http_api.add_routes(
            path="/generate",
            methods=[HttpMethod.POST],
            integration=audio_generation_controller_integration,
            authorizer=authorizer
        )
