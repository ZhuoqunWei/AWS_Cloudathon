from aws_cdk import (
    App, Stack,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns
)
from constructs import Construct

class BackendServiceStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # 1. Create a VPC with 2 AZs
        vpc = ec2.Vpc(self, "MyVpc", max_azs=2)

        # 2. Create an ECS Cluster inside the VPC
        cluster = ecs.Cluster(self, "MyCluster", vpc=vpc)

        # 3. Create a Fargate Service + Load Balancer for Product Service
        product_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self, "ProductService",
            cluster=cluster,
            cpu=256,
            memory_limit_mib=512,
            desired_count=1,
            listener_port=80,
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_registry("amazon/amazon-ecs-sample"),
                container_port=80
            ),
            public_load_balancer=True
        )

        # 4. Create another Fargate Service + Load Balancer for Order Service
        order_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self, "OrderService",
            cluster=cluster,
            cpu=256,
            memory_limit_mib=512,
            desired_count=1,
            listener_port=81,  # Use a different port
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_registry("amazon/amazon-ecs-sample"),
                container_port=80
            ),
            public_load_balancer=True
        )

app = App()
BackendServiceStack(app, "BackendServiceStack")
app.synth()
