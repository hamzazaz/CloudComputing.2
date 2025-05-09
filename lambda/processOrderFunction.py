import json
import boto3
from botocore.exceptions import ClientError

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Orders')

def lambda_handler(event, context):
    # Iterate through each record (message from SQS)
    for record in event.get('Records', []):
        try:
            # Log raw SQS body for debugging
            print("[DEBUG] Raw SQS body:", record['body'])
            
            # First, parse the outer SQS/SNS message
            body = json.loads(record['body'])  # The outer message from SQS

            # Retrieve the inner Message (double-encoded JSON)
            if 'Message' in body:
                message_str = body['Message']  # This is still a string, needs parsing
                try:
                    # Parse the inner Message
                    message = json.loads(message_str)
                    print("[DEBUG] Parsed message:", message)
                except json.JSONDecodeError:
                    print("Failed to parse inner JSON message.")
                    continue  # Skip this message and move to the next

                # Now that we have a parsed dictionary, extract values
                orderId = message.get("orderId")
                userId = message.get("userId")
                itemName = message.get("itemName")
                timestamp = message.get("timestamp")
                
                # Check if required fields are missing
                if None in [orderId, userId, itemName, timestamp]:
                    print("[SKIPPED] Missing required fields: ['orderId', 'userId', 'itemName', 'timestamp']")
                    continue  # Skip this record

                # Prepare the item to insert into DynamoDB
                order_data = {
                    'orderId': str(orderId),  # Ensure correct key names
                    'userId': str(userId),
                    'itemName': str(itemName),
                    'quantity': int(message.get('quantity', 1)),  # Default to 1 if not provided
                    'status': str(message.get('status', 'new')),  # Default to 'new' if not provided
                    'timestamp': str(timestamp)
                }

                # Log the item that will be inserted
                print("Putting item into DynamoDB:", order_data)

                # Insert the item into DynamoDB
                response = table.put_item(Item=order_data)
                print(f"PutItem succeeded: {response}")

        except Exception as e:
            print(f"Error processing record: {e}")
            continue  # Don't raise, continue processing other records

    return {'statusCode': 200}
