import json
import boto3
import os
import uuid
from datetime import datetime
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')

CHAT_CONFIG_BUCKET = os.getenv('CHAT_CONFIG_BUCKET', 'your-chat-config-bucket')
CHAT_SESSIONS_TABLE = os.getenv('CHAT_SESSIONS_TABLE', 'YourChatSessionsTable')

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

def fetch_chat_config(chat_config_id):
    """
    Fetch chat configuration from S3 bucket using the chat_config_id.
    """
    try:
        response = s3.get_object(Bucket=CHAT_CONFIG_BUCKET, Key=f'chat-configs/{chat_config_id}.json')
        config_data = response['Body'].read().decode('utf-8')
        return json.loads(config_data)
    except Exception as e:
        print(f"Error fetching chat config: {e}")
        raise e


def lambda_handler(event, context):
    try:
        # Parse the incoming event to get chat_config_id
        body = json.loads(event['body'])
        chat_config_id = body.get('chat_config_id')
        if not chat_config_id:
            print('chat_config_id is missing in the request body')
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'chat_config_id is required'})
            }

        print('Received chat_config_id:', chat_config_id)

        # Fetch chat configuration from S3
        print('Fetching chat config from S3 for chat_config_id:', chat_config_id)
        config = fetch_chat_config(chat_config_id)
        print('Fetched chat config from S3 for chat_config_id:', chat_config_id)

        # Generate a unique session ID and timestamp
        session_id = str(uuid.uuid4())
        created_at = datetime.utcnow().isoformat()

        # Prepare the session data
        session_item = {
            "session_id": session_id,
            "chat_config_id": chat_config_id,
            "title": config.get("title", "New Chat Session"),
            "model": config.get("model"),
            "system_prompt": config.get("systemPrompt"),
            "temperature":Decimal(str(config.get("temperature"))),
            "created_at": created_at,
            "messages": []  # empty history
        }

        # Store session in DynamoDB
        print('Storing session in DynamoDB:', session_item)
        table = dynamodb.Table(CHAT_SESSIONS_TABLE)
        table.put_item(Item=session_item)

        print('Session stored successfully')

        return _response(200, json.dumps({
                "sessionId": session_id,
                "createdAt": created_at
            }))

    except s3.exceptions.NoSuchKey:
        print(f"Chat config not found for chat_config_id: {chat_config_id}")
        return _response(400, json.dumps({"error": "Chat config not found"}))

    except Exception as e:
        print(f"Error in lambda_handler: {e}")
        return _response(500, json.dumps({"error": "Internal server error"}))





