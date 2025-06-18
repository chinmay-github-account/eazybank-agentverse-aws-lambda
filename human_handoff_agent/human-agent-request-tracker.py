import boto3
import json
import uuid
import os

# Initialize AWS resources outside the handler for reuse
dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ.get('DYNAMODB_TABLE_NAME')  # Read table name from environment variable
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    """
    This Lambda function processes messages from an SQS queue, stores the data
    in a DynamoDB table.
    """
    try:
        for record in event['Records']:
            message_body = json.loads(record['body'])  # Parse the SQS message body

            # Extract data from the message
            user_message = message_body.get('user_message')
            conversation_history = message_body.get('conversation_history')
            session_id = message_body.get('session_id')
            timestamp = message_body.get('timestamp')

            # Generate a UUID for the DynamoDB partition key
            item_id = str(uuid.uuid4())

            # Create the DynamoDB item
            item = {
                'id': item_id,  # Partition key
                'user_message': user_message,
                'conversation_history': conversation_history,
                'session_id': session_id,
                'timestamp': timestamp
            }

            # Write the item to DynamoDB
            table.put_item(Item=item)

            print(f"Successfully processed message and stored in DynamoDB with ID: {item_id}")

        return {
            'statusCode': 200,
            'body': json.dumps('Successfully processed SQS messages, and stored in DynamoDB')
        }

    except Exception as e:
        print(f"Error processing SQS message: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error processing SQS message: {e}')
        }
