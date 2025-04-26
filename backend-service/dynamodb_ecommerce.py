"""
E-commerce DynamoDB Manager
Complete utility for working with Products, NewOrders and Users tables in DynamoDB
"""
import boto3
import json
import uuid
from datetime import datetime
from botocore.exceptions import ClientError
from decimal import Decimal
import time

class EcommerceDynamoDB:
    def __init__(self, region_name='us-east-1'):
        """Initialize DynamoDB resource"""
        self.dynamodb = boto3.resource('dynamodb', region_name=region_name)
        self.client = boto3.client('dynamodb', region_name=region_name)

    def user_view_product(self, product_id):
        """Get product by ID"""
        return self.get_product(product_id)

    def get_product(self, product_id):
        """Get product by ID from DynamoDB and print all related information"""
        table = self.dynamodb.Table('Products')
        try:
            response = table.get_item(Key={'product_id': product_id})
            product = response.get('Item')  # Fetch the product item if found
            
            # Print all related product information
            if product:
                print("Product Information:")
                for key, value in product.items():
                    print(f"{key}: {value}")
            else:
                print(f"Product with ID {product_id} not found.")
            
            return product
        
        except Exception as e:
            print(f"Error fetching product: {e}")
            return None
    
    # ========== PRODUCT OPERATIONS ==========
    
    def create_product(self, name, price, category=None, stock=0, description=None, image_url=None):
        """Create a new product"""
        table = self.dynamodb.Table('Products')
        product_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        item = {
            'product_id': product_id,
            'name': name,
            'price': Decimal(str(price)),
            'stock': stock,
            'created_at': timestamp,
        }
        
        if category:
            item['category'] = category
        if description:
            item['description'] = description
        if image_url:
            item['image_url'] = image_url
            
        table.put_item(Item=item)
        return product_id
    
    def get_product(self, product_id):
        """Get product by ID"""
        table = self.dynamodb.Table('Products')
        response = table.get_item(Key={'product_id': product_id})
        return response.get('Item')
    
    def update_product_stock(self, product_id, new_stock):
        """Update product stock quantity"""
        table = self.dynamodb.Table('Products')
        response = table.update_item(
            Key={'product_id': product_id},
            UpdateExpression="set stock = :s",
            ExpressionAttributeValues={':s': new_stock},
            ReturnValues="UPDATED_NEW"
        )
        return response

    def get_products_by_category(self, category, min_price=None, max_price=None):
        """Get products by category with optional price range filtering"""
        table = self.dynamodb.Table('Products')
        
        key_condition = "category = :cat"
        expression_values = {':cat': category}
        
        if min_price is not None and max_price is not None:
            key_condition += " AND price BETWEEN :min AND :max"
            expression_values[':min'] = Decimal(str(min_price))
            expression_values[':max'] = Decimal(str(max_price))
        elif min_price is not None:
            key_condition += " AND price >= :min"
            expression_values[':min'] = Decimal(str(min_price))
        elif max_price is not None:
            key_condition += " AND price <= :max"
            expression_values[':max'] = Decimal(str(max_price))
        
        response = table.query(
            IndexName='CategoryPriceIndex',
            KeyConditionExpression=key_condition,
            ExpressionAttributeValues=expression_values
        )
        
        return response['Items']
    
    # ========== USER OPERATIONS ==========

    def create_user(self, name, email, address=None):
        """Create a new user"""
        table = self.dynamodb.Table('Users')
        user_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        item = {
            'user_id': user_id,
            'name': name,
            'email': email,
            'created_at': timestamp
        }
        
        if address and isinstance(address, dict):
            item['address'] = address
            
        table.put_item(Item=item)
        return user_id
    
    def get_user(self, user_id):
        """Get user by ID"""
        table = self.dynamodb.Table('Users')
        response = table.get_item(Key={'user_id': user_id})
        return response.get('Item')
    
    def update_user_address(self, user_id, address):
        """Update user's address"""
        table = self.dynamodb.Table('Users')
        response = table.update_item(
            Key={'user_id': user_id},
            UpdateExpression="set address = :a",
            ExpressionAttributeValues={':a': address},
            ReturnValues="UPDATED_NEW"
        )
        return response

    # ========== NEW ORDER OPERATIONS ==========

    def create_order(self, user_id, order_items, total_amount):
        """Create a new order"""
        table = self.dynamodb.Table('NewOrders')
        order_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        for item in order_items:
            if 'price' in item and not isinstance(item['price'], Decimal):
                item['price'] = Decimal(str(item['price']))
        
        item = {
            'order_id': order_id,
            'user_id': user_id,
            'order_items': order_items,
            'total_amount': Decimal(str(total_amount)),
            'order_status': 'PENDING',
            'created_at': timestamp
        }
            
        table.put_item(Item=item)
        return order_id
    
    def get_order(self, order_id):
        """Get order by ID"""
        table = self.dynamodb.Table('NewOrders')
        response = table.get_item(Key={'order_id': order_id})
        return response.get('Item')
    
    def get_user_orders(self, user_id, start_date=None, end_date=None):
        """Get all orders for a specific user with optional date filtering"""
        table = self.dynamodb.Table('NewOrders')
        
        key_condition = "user_id = :uid"
        expression_values = {':uid': user_id}
        
        if start_date and end_date:
            key_condition += " AND created_at BETWEEN :start AND :end"
            expression_values[':start'] = start_date
            expression_values[':end'] = end_date
        elif start_date:
            key_condition += " AND created_at >= :start"
            expression_values[':start'] = start_date
        elif end_date:
            key_condition += " AND created_at <= :end"
            expression_values[':end'] = end_date
        
        response = table.query(
            IndexName='UserOrderIndex',
            KeyConditionExpression=key_condition,
            ExpressionAttributeValues=expression_values
        )
        
        return response['Items']
    
    def update_order_status(self, order_id, new_status):
        """Update order status"""
        table = self.dynamodb.Table('NewOrders')
        response = table.update_item(
            Key={'order_id': order_id},
            UpdateExpression="set order_status = :s",
            ExpressionAttributeValues={':s': new_status},
            ReturnValues="UPDATED_NEW"
        )
        return response

    # ========== TABLE UTILITIES ==========

    def create_tables_if_not_exist(self):
        """Create all required tables if they don't exist"""
        existing_tables = self.client.list_tables()['TableNames']
        
        # Create Products table if it doesn't exist
        if 'Products' not in existing_tables:
            print("Creating Products table...")
            self.client.create_table(
                TableName='Products',
                KeySchema=[
                    {'AttributeName': 'product_id', 'KeyType': 'HASH'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'product_id', 'AttributeType': 'S'},
                    {'AttributeName': 'category', 'AttributeType': 'S'},
                    {'AttributeName': 'price', 'AttributeType': 'N'}
                ],
                GlobalSecondaryIndexes=[
                    {
                        'IndexName': 'CategoryPriceIndex',
                        'KeySchema': [
                            {'AttributeName': 'category', 'KeyType': 'HASH'},
                            {'AttributeName': 'price', 'KeyType': 'RANGE'}
                        ],
                        'Projection': {'ProjectionType': 'ALL'},
                        'ProvisionedThroughput': {
                            'ReadCapacityUnits': 5,
                            'WriteCapacityUnits': 5
                        }
                    }
                ],
                BillingMode='PROVISIONED',
                ProvisionedThroughput={
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            )
            print("Waiting for Products table to be created...")
            self._wait_for_table('Products')
        
        # Create Users table if it doesn't exist
        if 'Users' not in existing_tables:
            print("Creating Users table...")
            self.client.create_table(
                TableName='Users',
                KeySchema=[
                    {'AttributeName': 'user_id', 'KeyType': 'HASH'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'user_id', 'AttributeType': 'S'}
                ],
                BillingMode='PROVISIONED',
                ProvisionedThroughput={
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            )
            print("Waiting for Users table to be created...")
            self._wait_for_table('Users')
        
        # Create NewOrders table if it doesn't exist
        if 'NewOrders' not in existing_tables:
            print("Creating NewOrders table...")
            self.client.create_table(
                TableName='NewOrders',
                KeySchema=[
                    {'AttributeName': 'order_id', 'KeyType': 'HASH'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'order_id', 'AttributeType': 'S'},
                    {'AttributeName': 'user_id', 'AttributeType': 'S'},
                    {'AttributeName': 'created_at', 'AttributeType': 'S'}
                ],
                GlobalSecondaryIndexes=[
                    {
                        'IndexName': 'UserOrderIndex',
                        'KeySchema': [
                            {'AttributeName': 'user_id', 'KeyType': 'HASH'},
                            {'AttributeName': 'created_at', 'KeyType': 'RANGE'}
                        ],
                        'Projection': {'ProjectionType': 'ALL'},
                        'ProvisionedThroughput': {
                            'ReadCapacityUnits': 5,
                            'WriteCapacityUnits': 5
                        }
                    }
                ],
                BillingMode='PROVISIONED',
                ProvisionedThroughput={
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            )
            print("Waiting for NewOrders table to be created...")
            self._wait_for_table('NewOrders')
            
        print("All tables created successfully!")

    def _wait_for_table(self, table_name, max_attempts=10):
        """Wait for a table to be created"""
        for i in range(max_attempts):
            try:
                table = self.dynamodb.Table(table_name)
                if table.table_status == 'ACTIVE':
                    return True
                print(f"Table status: {table.table_status}, waiting...")
                time.sleep(5)
            except Exception as e:
                print(f"Error checking table status: {e}")
                time.sleep(5)
        
        raise TimeoutError(f"Table {table_name} did not become active within {max_attempts} attempts")

    def populate_sample_data(self):
        """Add sample data to tables for testing"""
        # Create sample products
        products = [
            {"name": "Smartphone X", "price": 999.99, "category": "Electronics", "stock": 50, 
             "description": "Latest smartphone with advanced features"},
            {"name": "Laptop Pro", "price": 1499.99, "category": "Electronics", "stock": 30, 
             "description": "Professional laptop for developers"},
            {"name": "Wireless Earbuds", "price": 129.99, "category": "Electronics", "stock": 100, 
             "description": "High-quality wireless earbuds"},
            {"name": "Cotton T-Shirt", "price": 19.99, "category": "Clothing", "stock": 200, 
             "description": "Comfortable cotton t-shirt"},
            {"name": "Jeans", "price": 59.99, "category": "Clothing", "stock": 150, 
             "description": "Classic blue jeans"},
            {"name": "Running Shoes", "price": 89.99, "category": "Footwear", "stock": 80, 
             "description": "Lightweight running shoes"}
        ]
        
        product_ids = []
        for product in products:
            product_id = self.create_product(**product)
            product_ids.append(product_id)
            print(f"Created product: {product['name']} with ID: {product_id}")
        
        # Create sample users
        users = [
            {"name": "John Doe", "email": "john@example.com", 
             "address": {"street": "123 Main St", "city": "Seattle", "state": "WA", "zip": "98101"}},
            {"name": "Jane Smith", "email": "jane@example.com", 
             "address": {"street": "456 Park Ave", "city": "New York", "state": "NY", "zip": "10001"}}
        ]
        
        user_ids = []
        for user in users:
            user_id = self.create_user(**user)
            user_ids.append(user_id)
            print(f"Created user: {user['name']} with ID: {user_id}")
        
        # Create sample orders
        if product_ids and user_ids:
            # Order for first user
            order_items1 = [
                {"product_id": product_ids[0], "quantity": 1, "price": 999.99},
                {"product_id": product_ids[2], "quantity": 2, "price": 129.99}
            ]
            order_id1 = self.create_order(user_ids[0], order_items1, 1259.97)
            print(f"Created order for user {users[0]['name']} with ID: {order_id1}")
            
            # Order for second user
            order_items2 = [
                {"product_id": product_ids[1], "quantity": 1, "price": 1499.99},
                {"product_id": product_ids[4], "quantity": 1, "price": 59.99}
            ]
            order_id2 = self.create_order(user_ids[1], order_items2, 1559.98)
            print(f"Created order for user {users[1]['name']} with ID: {order_id2}")
            
        return {
            "product_ids": product_ids,
            "user_ids": user_ids
        }

# Usage example
if __name__ == "__main__":
    db = EcommerceDynamoDB()
    
    # Create tables if they don't exist
    db.create_tables_if_not_exist()
    
    # Add sample data
    sample_data = db.populate_sample_data()
    
    # Example: Get product by ID
    if sample_data["product_ids"]:
        product = db.get_product(sample_data["product_ids"][0])
        print(f"Retrieved product: {json.dumps(product, default=str)}")
    
    # Example: Get user orders
    if sample_data["user_ids"]:
        orders = db.get_user_orders(sample_data["user_ids"][0])
        print(f"User orders: {json.dumps(orders, default=str)}")
