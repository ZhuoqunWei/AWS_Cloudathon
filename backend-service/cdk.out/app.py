from flask import Flask, jsonify, request
from aws_cdk import (
    App, Stack,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns
)
from constructs import Construct
from dynamodb_ecommerce import EcommerceDynamoDB  # Assuming you've written the DynamoDB interaction methods

# Create Flask application
app = Flask(__name__)

# Initialize the DynamoDB interaction class
db = EcommerceDynamoDB()

class BackendServiceStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # 1. Create a VPC with 2 Availability Zones (AZs)
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
            public_load_balancer=True  # Expose the service via a public load balancer
        )

        # 4. Create another Fargate Service + Load Balancer for Order Service
        order_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self, "OrderService",
            cluster=cluster,
            cpu=256,
            memory_limit_mib=512,
            desired_count=1,
            listener_port=81,  # Use a different port for the Order Service
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_registry("amazon/amazon-ecs-sample"),
                container_port=80
            ),
            public_load_balancer=True  # Expose the service via a public load balancer
        )

# Flask route: User views product information
@app.route('/api/product/<product_id>', methods=['GET'])
def user_view_product(product_id):
    try:
        product = db.user_view_product(product_id)  # Use the method from DynamoDB class
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        return jsonify(product)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Flask route: User adds product to a new order
@app.route('/api/order', methods=['POST'])
def user_add_product_to_new_order():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        product_id = data.get('product_id')
        quantity = data.get('quantity')

        if not user_id or not product_id or not quantity:
            return jsonify({'error': 'Missing required parameters'}), 400
        
        order_id = db.user_add_product_to_new_order(user_id, product_id, quantity)
        return jsonify({'order_id': order_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Run Flask application
if __name__ == "__main__":
    app.run(debug=True)