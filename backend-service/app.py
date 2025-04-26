from flask import Flask, jsonify, request
from dynamodb_ecommerce import EcommerceDynamoDB  # Assuming you've written the DynamoDB interaction methods

# Create Flask application
app = Flask(__name__)

# Initialize the DynamoDB interaction class
db = EcommerceDynamoDB()

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

# Run Flask application, listen on port 80 (to match ECS service)
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=80)