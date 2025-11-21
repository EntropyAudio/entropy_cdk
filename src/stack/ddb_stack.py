from aws_cdk import Stack
from aws_cdk.aws_dynamodb import Table, Attribute, AttributeType, BillingMode
from constructs import Construct

class DDBStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        self.audio_metadata_table = Table(
            self,
            id="AudioMetadata",
            table_name="AudioMetadata",
            partition_key=Attribute(name="user_id", type=AttributeType.STRING),
            sort_key=Attribute(name="creation_date", type=AttributeType.NUMBER),
            billing_mode=BillingMode.PAY_PER_REQUEST,
            point_in_time_recovery=True,
        )

        # user who generated the audio
        # job execution id of audio
        # s3 file path of audio
        # whether the audio was selected
        # prompt used to generate audio + other conditioning data
        # creation date
        # model id/version - saved into s3

        # sample rate
        # duration
