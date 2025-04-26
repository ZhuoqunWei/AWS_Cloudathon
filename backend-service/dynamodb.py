import boto3
from boto3.dynamodb.conditions import Key

# Create a DynamoDB client
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

# Connect to your Products table
table = dynamodb.Table('Products')

# 1. Read item
def get_product(product_id):
    response = table.get_item(
        Key={
            'product_id': product_id
        }
    )
    return response.get('Item', None)

# 2. Update item (e.g., decrease stock after an order)
def update_product_stock(product_id, quantity_sold):
    response = table.update_item(
        Key={
            'product_id': product_id
        },
        UpdateExpression="SET stock = stock - :qty",
        ExpressionAttributeValues={
            ':qty': quantity_sold
        },
        ReturnValues="UPDATED_NEW"
    )
    return response

# Example Usage
if __name__ == "__main__":
    product = get_product('p123')
    print("Product Info:", product)
    
    updated = update_product_stock('p123', 1)
    print("Updated Stock Info:", updated)
