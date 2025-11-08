from aws_cdk import Stack, CfnOutput, Duration
from constructs import Construct
from dataclasses import dataclass
from .lambda_stack import LambdaStack
from aws_cdk.aws_apigatewayv2 import HttpApi, CorsPreflightOptions, CorsHttpMethod, HttpMethod
from aws_cdk.aws_apigatewayv2_integrations import HttpLambdaIntegration

@dataclass
class APIGStackProps:
    lambda_stack: LambdaStack


class APIGStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, props: APIGStackProps, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

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
                max_age=Duration.days(10)
            )
        )

        http_api.add_routes(
            path="/generate",
            methods=[HttpMethod.POST],
            integration=audio_generation_controller_integration
        )
