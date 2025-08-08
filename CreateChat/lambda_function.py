import boto3
import json, os, uuid

# Create a new S3 client
s3 = boto3.client('s3')
BUCKET_NAME = os.getenv('BUCKET_NAME', "your-default-bucket-name")

def lambda_handler(event, context):

    try:
        body = json.loads(event['body'])

        # Validate required fields
        required_fileds = ['model', 'systemPrompt', 'temperature', 'title']
        if not all(field in body for field in required_fileds):
            print('Missing required fields in the request body')
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing required fields'})
            }

        print('Received request')
        # Generate a unique chat config ID
        chat_config_id = str(uuid.uuid4())

        # Build config
        config = {
            "chatConfigId": chat_config_id,
            "model": body["model"],
            "systemPrompt": body["systemPrompt"],
            "temperature": body["temperature"],
            "title": body["title"]
        }

        print('Saving chat config to S3')
        # Save the config to S3
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=f'chat-configs/{chat_config_id}.json',
            Body=json.dumps(config),
            ContentType='application/json'
        )

        print('Chat config saved successfully')

        # Return shareable URL
        frontend_base_url = os.environ.get("FRONTEND_BASE_URL", "https://yourdomain.com")
        shareable_url = f"{frontend_base_url}/chat/{chat_config_id}"

        # Return the chat config ID
        return _response(200, {
            "chatConfigId": chat_config_id,
            "shareableUrl": shareable_url
        })

    except Exception as e:
        print(f"Error processing request: {e}")
        return _response(500, {
            "error": "Internal server error"
        })

def _response(status_code, body_dict):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "POST,OPTIONS"
        },
        "body": json.dumps(body_dict)
    }

