import json
import boto3

client = boto3.client('dynamodb')

def lambda_handler(event, context):
    """
    Fetches user details from DynamoDB based on the phone number.

    Args:
        event (dict): Event data passed to the Lambda function.  This is expected to contain the phone number in the 'parameters' section.
        context (object): Lambda context object.

    Returns:
        dict: Response containing the user details or an error message, formatted for a Bedrock Agent.
    """

    try:
        phone_no = event['parameters'][0]['value']

        # Create a request syntax to retrieve data from the DynamoDB Table using GET Item method
        response = client.get_item(
            TableName='eazybank-applications', 
            Key={'phone_no': {'N': phone_no}}
        )

        if 'Item' in response:
            # Convert DynamoDB's format to a more readable JSON format
            item = response['Item']
            user_details = {}
            for key, value in item.items():
                user_details[key] = list(value.values())[0]
            print(user_details)

            response_body = {
                'application/json': {
                    'body': json.dumps(user_details)
                }
            }
        else:
            response_body = {
                'application/json': {
                    'body': json.dumps({'message': 'User not found'})
                }
            }
            
        action_response = {
            'actionGroup': event['actionGroup'],
            'apiPath': event['apiPath'],
            'httpMethod': event['httpMethod'],
            'httpStatusCode': 200,
            'responseBody': response_body
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

    except KeyError as e:
        print(f"Missing key in event: {e}")
        return {
            'statusCode': 400,
            'body': json.dumps({'message': f'Missing required parameter: {e}'})
        }
    except Exception as e:
        print(f"Error getting data from DynamoDB: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'message': f'Error retrieving user details: {e}'})
        }