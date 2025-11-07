import aws_cdk as core
import aws_cdk.assertions as assertions

from entropy_cdk.entropy_cdk_stack import EntropyCdkStack

# example tests. To run these tests, uncomment this file along with the example
# resource in entropy_cdk/entropy_cdk_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = EntropyCdkStack(app, "entropy-cdk")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
