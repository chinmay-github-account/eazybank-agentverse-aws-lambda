import boto3
import json
import os

# Initialize SNS client outside the handler
sns = boto3.client('sns')
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN')

def lambda_handler(event, context):
    """
    This Lambda function is triggered by DynamoDB Streams.
    It processes stream records and publishes relevant data to an SNS topic.
    """
    try:
        for record in event['Records']:
            # Check the event type (INSERT, MODIFY, REMOVE)
            event_name = record['eventName']

            if event_name == 'INSERT' or event_name == 'MODIFY':  # Process only inserts and updates

                # Extract the new image (the item after the change)
                new_image = record['dynamodb'].get('NewImage')

                if new_image:
                    # Extract relevant data from the NewImage attribute
                    user_message = new_image.get('user_message', {}).get('S')
                    conversation_history = new_image.get('conversation_history', {}).get('S')
                    session_id = new_image.get('session_id', {}).get('S')
                    timestamp = new_image.get('timestamp', {}).get('S')

                    # Create a message payload
                    message_payload = {
                        'user_message': user_message,
                        'conversation_history': conversation_history,
                        'session_id': session_id,
                        'timestamp': timestamp
                    }

                    # Publish the message to SNS
                    sns.publish(
                        TopicArn=SNS_TOPIC_ARN,
                        Message=json.dumps(message_payload),
                        Subject='Human Agent Request (via DynamoDB Streams)'
                    )

                    print(f"Successfully published message to SNS topic: {SNS_TOPIC_ARN}")

            elif event_name == 'REMOVE':
                # Optional: Handle delete events if needed
                print("Item removed from DynamoDB.  No SNS notification sent.")
            else:
                print(f"Unhandled event type: {event_name}")

        return {
            'statusCode': 200,
            'body': json.dumps('Successfully processed DynamoDB stream records and published to SNS.')
        }

    except Exception as e:
        print(f"Error processing DynamoDB stream record: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error processing DynamoDB stream record: {e}')
        }