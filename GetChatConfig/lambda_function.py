import boto3, json, os

s3 = boto3.client('s3')
BUCKET_NAME = os.getenv('BUCKET_NAME', 'my-default-bucket')  # Set a default bucket name if not provided

def _response(status_code, body_dict):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "GET,OPTIONS"
        },
        "body": json.dumps(body_dict)
    }

def lambda_handler(event, context):
    try:

        # Extract chat_config_id from the path parameters
        print('Extracting chat_config_id from event')
        chat_config_id = event['pathParameters']['chat_config_id']
        s3_key = f'chat-configs/{chat_config_id}.json'

        # Fetch the chat configuration from S3
        print(f'Fetching chat configuration from S3 bucket: {BUCKET_NAME}, key: {s3_key}')
        response = s3.get_object(Bucket=BUCKET_NAME, Key=s3_key)

        chat_config_data = response['Body'].read().decode('utf-8')
        print('Chat configuration fetched successfully')

        chat_config = json.loads(chat_config_data)

        # Return the chat configuration as a JSON response
        return _response(200, chat_config)

    except s3.exceptions.NoSuchKey:
        print(f'Chat configuration with ID {chat_config_id} not found in bucket {BUCKET_NAME}')
        return _response(404, {'error': 'Chat configuration not found'})

    except Exception as e:
        print(f'An error occurred: {str(e)}')
        return _response(500, {'error': 'Internal server error'})
