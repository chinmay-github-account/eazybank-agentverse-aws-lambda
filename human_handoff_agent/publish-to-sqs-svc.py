import json
import boto3
import os

def lambda_handler(event, context):
    """
    Handles requests, extracts data, sends to SQS, constructs a detailed response, and *explicitly logs the response*.
    """
    try:
        # Extract data from the event (passed by Bedrock Agent)
        try:
            request_body = event.get('requestBody', {})
            content = request_body.get('content', {})
            application_json = content.get('application/json', {})
            properties_list = application_json.get('properties', [])
        except (KeyError, TypeError) as e:
            print(f"Error parsing event structure: {e}")
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Invalid request body structure'})
            }

        # Function to extract value by name
        def get_value(name, properties):
            for prop in properties:
                if prop.get('name') == name:
                    return prop.get('value')
            return None  # Or an appropriate default value

        # Extract the values
        user_message = get_value('user_message', properties_list)
        conversation_history = get_value('conversation_history', properties_list)
        session_id = get_value('session_id', properties_list)
        timestamp = get_value('timestamp', properties_list)

        # Validate that required fields are present
        if not all([user_message, session_id, timestamp]):
            print(f"Missing one or more required parameters. Extracted values: user_message={user_message}, session_id={session_id}, timestamp={timestamp}")
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Missing required parameters'})
            }

        # Prepare the message for SQS
        message = {
            "user_message": user_message,
            "conversation_history": conversation_history,
            "session_id": session_id,
            "timestamp": timestamp
        }
        message_body = json.dumps(message)

        # Initialize SQS client
        sqs = boto3.client('sqs')

        # Get the SQS Queue URL from environment variable
        queue_url = os.environ.get('SQS_QUEUE_URL')

        if not queue_url:
            print("SQS_QUEUE_URL environment variable not set.")
            return {
                'statusCode': 500,
                'body': json.dumps({'message': 'SQS Queue URL not configured'})
            }

        # Send message to SQS FIFO queue
        response = sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=message_body,
            MessageGroupId=session_id  # Required for FIFO queues.  Crucially, use session_id for grouping.
            # MessageDeduplicationId=  # Only required if content-based deduplication is disabled
        )

        # Construct the response body as a dictionary
        response_body_content = {
            'message': 'Data sent to SQS successfully!'
        }

        action_response = {
            'actionGroup': event['actionGroup'],
            'apiPath': event['apiPath'],
            'httpMethod': event['httpMethod'],
            'httpStatusCode': 200,
            'responseBody': {
                'application/json': {
                    'body': json.dumps(response_body_content)
                }
            }
        }

        session_attributes = event.get('sessionAttributes', {})
        prompt_session_attributes = event.get('promptSessionAttributes', {})

        api_response = {
            'messageVersion': '1.0',
            'response': action_response,
            'sessionAttributes': session_attributes,
            'promptSessionAttributes': prompt_session_attributes
        }

        print(f"Lambda Response (final): {json.dumps(api_response)}")
        return api_response


    except Exception as e:
        print(f"Error processing request: {e}")
        error_response_body = {'message': f'Error processing request: {str(e)}'}

        action_response = {
            'actionGroup': event['actionGroup'],
            'apiPath': event['apiPath'],
            'httpMethod': event['httpMethod'],
            'httpStatusCode': 500,
            'responseBody': {
                'application/json': {
                    'body': json.dumps(error_response_body)
                }
            }
        }

        session_attributes = event.get('sessionAttributes', {})
        prompt_session_attributes = event.get('promptSessionAttributes', {})

        api_response = {
            'messageVersion': '1.0',
            'response': action_response,
            'sessionAttributes': session_attributes,
            'promptSessionAttributes': prompt_session_attributes
        }
        return api_response
