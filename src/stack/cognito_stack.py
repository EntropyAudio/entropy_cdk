from aws_cdk import Stack, RemovalPolicy
from aws_cdk.aws_secretsmanager import Secret
from aws_cdk.aws_cognito import (
    UserPool,
    SignInAliases,
    StandardAttributes,
    StandardAttribute,
    PasswordPolicy,
    AccountRecovery,
    OAuthScope,
    UserPoolIdentityProviderGoogle,
    ProviderAttribute,
    UserPoolClientIdentityProvider,
    OAuthFlows,
    OAuthSettings,
)
from constructs import Construct


class CognitoStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        self.user_pool = UserPool(
            self,
            id="EntropyAudioUsers",
            user_pool_name="EntropyAudioUsers",
            self_sign_up_enabled=True,
            sign_in_aliases=SignInAliases(email=True),
            standard_attributes=StandardAttributes(
                email=StandardAttribute(required=True, mutable=True),
                given_name=StandardAttribute(required=False, mutable=True),
                family_name=StandardAttribute(required=False, mutable=True)
            ),
            password_policy=PasswordPolicy(
                min_length=8,
                require_digits=True,
                require_lowercase=True,
                require_uppercase=True,
                require_symbols=False,
            ),
            account_recovery=AccountRecovery.EMAIL_ONLY,
            removal_policy=RemovalPolicy.DESTROY,
        )

        google_oauth_secret = Secret.from_secret_name_v2(
            self,
            id="GoogleOauthClientSecret",
            secret_name="GoogleOauthClientSecret"
        )

        google_provider = UserPoolIdentityProviderGoogle(
            self,
            "GoogleProvider",
            client_id="566752463670-bqo66imnsmikr4fh45ljf03sjbk2umd0.apps.googleusercontent.com",
            client_secret_value=google_oauth_secret.secret_value_from_json("GoogleOauthClientSecret"),
            user_pool=self.user_pool,
            attribute_mapping={
                "email": ProviderAttribute.GOOGLE_EMAIL,
            },
            scopes=["profile", "email", "openid"]
        )

        self.user_pool.add_domain(
            "CognitoDomain",
            cognito_domain={
                "domain_prefix": "entropy-audio"
            }
        )

        self.user_pool_client = self.user_pool.add_client(
            id="CognitoClient",
            generate_secret=False,
            o_auth=OAuthSettings(
                flows=OAuthFlows(
                    authorization_code_grant=True
                ),
                scopes=[OAuthScope.OPENID, OAuthScope.EMAIL, OAuthScope.PROFILE],
                callback_urls=[
                    "http://localhost:4200/",
                    "https://entropyaudio.io/"
                ],
                logout_urls=[
                    "http://localhost:4200/",
                    "https://entropyaudio.io/"
                ]
            ),
            supported_identity_providers=[
                UserPoolClientIdentityProvider.COGNITO,
                UserPoolClientIdentityProvider.GOOGLE
            ]
        )

        self.user_pool_client.node.add_dependency(google_provider)
