"""
Script to add more orders to the e-commerce DynamoDB database
"""
import boto3
import uuid
from decimal import Decimal
from datetime import datetime, timedelta
import random
import json

# Import your EcommerceDynamoDB class if available
# from ecommerce_dynamodb import EcommerceDynamoDB

# If you're having issues with the import, I'm including a simplified version here
class SimplifiedEcommerceDB:
    def __init__(self, region_name='us-east-1'):
        """Initialize DynamoDB resource"""
        self.dynamodb = boto3.resource('dynamodb', region_name=region_name)
        self.client = boto3.client('dynamodb', region_name=region_name)
    
    def create_order(self, user_id, order_items, total_amount, order_status="PENDING"):
        """Create a new order"""
        table = self.dynamodb.Table('Orders')
        order_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        # Convert any float prices to Decimal
        for item in order_items:
            if 'price' in item and not isinstance(item['price'], Decimal):
                item['price'] = Decimal(str(item['price']))
        
        item = {
            'order_id': order_id,
            'user_id': user_id,
            'order_items': order_items,
            'total_amount': Decimal(str(total_amount)),
            'order_status': order_status,
            'created_at': timestamp
        }
            
        try:
            table.put_item(Item=item)
            print(f"Successfully created order: {order_id}")
            return order_id
        except Exception as e:
            print(f"Error creating order: {e}")
            return None
    
    def get_all_users(self):
        """Get all users from the database"""
        try:
            table = self.dynamodb.Table('Users')
            response = table.scan()
            return response.get('Items', [])
        except Exception as e:
            print(f"Error getting users: {e}")
            return []
    
    def get_all_products(self):
        """Get all products from the database"""
        try:
            table = self.dynamodb.Table('Products')
            response = table.scan()
            return response.get('Items', [])
        except Exception as e:
            print(f"Error getting products: {e}")
            return []

def generate_random_orders(db, num_orders=10):
    """Generate random orders for existing users and products"""
    # Get all users and products
    users = db.get_all_users()
    products = db.get_all_products()
    
    if not users:
        print("No users found in the database. Please add users first.")
        return
    
    if not products:
        print("No products found in the database. Please add products first.")
        return
    
    # Order statuses
    statuses = ["PENDING", "PROCESSING", "SHIPPED", "DELIVERED", "CANCELLED"]
    
    # Generate random orders
    orders_created = 0
    for _ in range(num_orders):
        # Select a random user
        user = random.choice(users)
        user_id = user['user_id']
        
        # Determine number of items in this order (1-5)
        num_items = random.randint(1, 5)
        
        # Select random products for this order
        order_products = random.sample(products, min(num_items, len(products)))
        
        # Create order items
        order_items = []
        total_amount = Decimal('0')
        
        for product in order_products:
            # Determine quantity for this product (1-3)
            quantity = random.randint(1, 3)
            
            # Calculate item price
            item_price = Decimal(str(product['price']))
            
            # Add to order items
            order_items.append({
                'product_id': product['product_id'],
                'quantity': quantity,
                'price': item_price,
                'name': product['name']  # Include product name for convenience
            })
            
            # Add to total amount
            total_amount += item_price * Decimal(str(quantity))
        
        # Select a random status
        order_status = random.choice(statuses)
        
        # Create the order
        order_id = db.create_order(user_id, order_items, total_amount, order_status)
        
        if order_id:
            orders_created += 1
    
    print(f"Successfully created {orders_created} new orders")

def create_orders_with_specific_data(db):
    """Create orders with specific data for testing"""
    # You can modify this function to create orders with specific data
    # This is useful for testing specific scenarios
    
    # Example: Create an order for a specific user with specific products
    try:
        # Get first user and a few products (modify to use specific IDs if needed)
        users = db.get_all_users()
        products = db.get_all_products()
        
        if not users or not products:
            print("No users or products found")
            return
        
        user_id = users[0]['user_id']
        
        # Create a large order with multiple products
        order_items = [
            {
                'product_id': products[0]['product_id'],
                'quantity': 2,
                'price': Decimal(str(products[0]['price'])),
                'name': products[0]['name']
            }
        ]
        
        if len(products) > 1:
            order_items.append({
                'product_id': products[1]['product_id'],
                'quantity': 1,
                'price': Decimal(str(products[1]['price'])),
                'name': products[1]['name']
            })
        
        # Calculate total
        total_amount = sum(item['price'] * Decimal(str(item['quantity'])) for item in order_items)
        
        # Create a SHIPPED order
        db.create_order(user_id, order_items, total_amount, "SHIPPED")
        
        # Create orders with different statuses
        statuses = ["PENDING", "PROCESSING", "DELIVERED", "CANCELLED"]
        for status in statuses:
            # Adjust quantity for variation
            order_items[0]['quantity'] = random.randint(1, 5)
            if len(order_items) > 1:
                order_items[1]['quantity'] = random.randint(1, 3)
            
            # Recalculate total
            total_amount = sum(item['price'] * Decimal(str(item['quantity'])) for item in order_items)
            
            # Create the order
            db.create_order(user_id, order_items, total_amount, status)
        
        print("Created specific test orders successfully")
    except Exception as e:
        print(f"Error creating specific orders: {e}")

def create_historical_orders(db, num_days=30):
    """Create orders with timestamps spread over a period of time"""
    users = db.get_all_users()
    products = db.get_all_products()
    
    if not users or not products:
        print("No users or products found")
        return
    
    current_time = datetime.utcnow()
    
    # Create orders spread over the specified number of days
    for day in range(num_days):
        # Set timestamp for this order
        order_time = current_time - timedelta(days=day, 
                                              hours=random.randint(0, 23),
                                              minutes=random.randint(0, 59))
        order_timestamp = order_time.isoformat()
        
        # Select a random user
        user = random.choice(users)
        user_id = user['user_id']
        
        # Determine number of items (1-3)
        num_items = random.randint(1, 3)
        
        # Select random products
        order_products = random.sample(products, min(num_items, len(products)))
        
        # Create order items
        order_items = []
        total_amount = Decimal('0')
        
        for product in order_products:
            quantity = random.randint(1, 2)
            item_price = Decimal(str(product['price']))
            
            order_items.append({
                'product_id': product['product_id'],
                'quantity': quantity,
                'price': item_price,
                'name': product['name']
            })
            
            total_amount += item_price * Decimal(str(quantity))
        
        # Determine a reasonable status based on age of order
        if day < 2:
            status = random.choice(["PENDING", "PROCESSING"])
        elif day < 7:
            status = random.choice(["PROCESSING", "SHIPPED", "DELIVERED"])
        else:
            status = random.choice(["DELIVERED", "CANCELLED"])
        
        # Create order directly using table to include custom timestamp
        table = db.dynamodb.Table('Orders')
        order_id = str(uuid.uuid4())
        
        try:
            item = {
                'order_id': order_id,
                'user_id': user_id,
                'order_items': order_items,
                'total_amount': total_amount,
                'order_status': status,
                'created_at': order_timestamp
            }
            
            table.put_item(Item=item)
            print(f"Created historical order from {order_timestamp} with status {status}")
        except Exception as e:
            print(f"Error creating historical order: {e}")

if __name__ == "__main__":
    # Change the region if needed
    db = SimplifiedEcommerceDB(region_name='us-east-1')
    
    # Uncomment the function you want to use:
    
    # Generate random orders
    generate_random_orders(db, num_orders=15)
    
    # Create specific test orders
    # create_orders_with_specific_data(db)
    
    # Create historical orders over the past 30 days
    # create_historical_orders(db, num_days=30)
    
    print("Order creation completed!")