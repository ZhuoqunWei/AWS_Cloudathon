"""
Custom Order Creator for DynamoDB
Create specific orders with precise control for testing and demonstration
"""
import boto3
import uuid
from decimal import Decimal
from datetime import datetime, timedelta
import json

# Configure your AWS region
REGION = 'us-east-1'

class OrderCreator:
    def __init__(self, region_name=REGION):
        """Initialize with AWS region"""
        self.dynamodb = boto3.resource('dynamodb', region_name=region_name)
        self.orders_table = self.dynamodb.Table('Orders')
        self.products_table = self.dynamodb.Table('Products')
        self.users_table = self.dynamodb.Table('Users')
    
    def get_user_by_email(self, email):
        """Find a user by email address"""
        response = self.users_table.scan(
            FilterExpression="email = :email",
            ExpressionAttributeValues={':email': email}
        )
        
        users = response.get('Items', [])
        if users:
            return users[0]
        return None
    
    def get_product_by_name(self, name):
        """Find a product by name (partial match)"""
        response = self.products_table.scan(
            FilterExpression="contains(#name, :name)",
            ExpressionAttributeNames={'#name': 'name'},
            ExpressionAttributeValues={':name': name}
        )
        
        products = response.get('Items', [])
        if products:
            return products[0]
        return None
    
    def list_all_users(self):
        """List all users in the database"""
        response = self.users_table.scan()
        users = response.get('Items', [])
        
        print("\n=== Available Users ===")
        for i, user in enumerate(users):
            print(f"{i+1}. {user.get('name')} ({user.get('email')}) - ID: {user.get('user_id')}")
        
        return users
    
    def list_all_products(self):
        """List all products in the database"""
        response = self.products_table.scan()
        products = response.get('Items', [])
        
        print("\n=== Available Products ===")
        for i, product in enumerate(products):
            print(f"{i+1}. {product.get('name')} - ${product.get('price')} - ID: {product.get('product_id')}")
        
        return products
    
    def create_custom_order(self, user_id, order_items, status="PENDING", days_ago=0):
        """
        Create a custom order with specific details
        
        Args:
            user_id: The ID of the user placing the order
            order_items: List of dictionaries with product_id, quantity, price
            status: Order status (PENDING, PROCESSING, SHIPPED, DELIVERED, CANCELLED)
            days_ago: How many days in the past to date the order
        
        Returns:
            order_id: The ID of the created order
        """
        # Generate order ID
        order_id = str(uuid.uuid4())
        
        # Set timestamp
        if days_ago > 0:
            timestamp = (datetime.utcnow() - timedelta(days=days_ago)).isoformat()
        else:
            timestamp = datetime.utcnow().isoformat()
        
        # Calculate total amount
        total_amount = sum(
            Decimal(str(item['price'])) * Decimal(str(item['quantity'])) 
            for item in order_items
        )
        
        # Create order object
        order = {
            'order_id': order_id,
            'user_id': user_id,
            'order_items': order_items,
            'total_amount': total_amount,
            'order_status': status,
            'created_at': timestamp
        }
        
        # Save to DynamoDB
        try:
            self.orders_table.put_item(Item=order)
            print(f"Successfully created order {order_id} with status {status}")
            return order_id
        except Exception as e:
            print(f"Error creating order: {e}")
            return None
    
    def create_interactive_order(self):
        """Create an order interactively by prompting for details"""
        # List users and products
        users = self.list_all_users()
        products = self.list_all_products()
        
        if not users or not products:
            print("Error: Need users and products to create an order")
            return
        
        # Select user
        try:
            user_index = int(input("\nEnter user number: ")) - 1
            user = users[user_index]
            user_id = user['user_id']
            print(f"Selected user: {user['name']}")
        except (ValueError, IndexError):
            print("Invalid selection")
            return
        
        # Build order items
        order_items = []
        while True:
            try:
                # Select product
                product_index = int(input("\nEnter product number (or 0 to finish): ")) - 1
                
                if product_index < 0:
                    break
                
                product = products[product_index]
                
                # Get quantity
                quantity = int(input(f"Quantity of {product['name']}: "))
                
                if quantity <= 0:
                    print("Quantity must be positive")
                    continue
                
                # Add to order items
                order_items.append({
                    'product_id': product['product_id'],
                    'quantity': quantity,
                    'price': product['price'],
                    'name': product['name']
                })
                
                print(f"Added {quantity}x {product['name']} to order")
                
            except (ValueError, IndexError):
                print("Invalid selection")
        
        if not order_items:
            print("Order cancelled - no items added")
            return
        
        # Get order status
        statuses = ["PENDING", "PROCESSING", "SHIPPED", "DELIVERED", "CANCELLED"]
        print("\nAvailable statuses:")
        for i, status in enumerate(statuses):
            print(f"{i+1}. {status}")
        
        try:
            status_index = int(input("Enter status number: ")) - 1
            status = statuses[status_index]
        except (ValueError, IndexError):
            print("Invalid status, using PENDING")
            status = "PENDING"
        
        # Get order date
        try:
            days_ago = int(input("Days ago (0 for today): "))
        except ValueError:
            days_ago = 0
        
        # Create the order
        self.create_custom_order(user_id, order_items, status, days_ago)

# Example of creating specific orders
def create_example_orders():
    creator = OrderCreator()
    
    # List available users and products
    users = creator.list_all_users()
    products = creator.list_all_products()
    
    if not users or not products:
        print("Error: Need users and products in the database first")
        return
    
    # Get the first user
    user = users[0]
    user_id = user['user_id']
    
    # Create a large order with multiple products
    if len(products) >= 3:
        large_order_items = [
            {
                'product_id': products[0]['product_id'],
                'quantity': 2,
                'price': products[0]['price'],
                'name': products[0]['name']
            },
            {
                'product_id': products[1]['product_id'],
                'quantity': 1,
                'price': products[1]['price'],
                'name': products[1]['name']
            },
            {
                'product_id': products[2]['product_id'],
                'quantity': 3,
                'price': products[2]['price'],
                'name': products[2]['name']
            }
        ]
        
        creator.create_custom_order(user_id, large_order_items, "PROCESSING", 1)
    
    # Create orders with different statuses
    if products:
        for status, days in [
            ("PENDING", 0),
            ("PROCESSING", 2),
            ("SHIPPED", 5),
            ("DELIVERED", 10),
            ("CANCELLED", 15)
        ]:
            order_items = [{
                'product_id': products[0]['product_id'],
                'quantity': 1,
                'price': products[0]['price'],
                'name': products[0]['name']
            }]
            
            creator.create_custom_order(user_id, order_items, status, days)
    
    print("Created example orders successfully")

if __name__ == "__main__":
    # Create example orders
    # create_example_orders()
    
    # OR create orders interactively
    creator = OrderCreator()
    creator.create_interactive_order()