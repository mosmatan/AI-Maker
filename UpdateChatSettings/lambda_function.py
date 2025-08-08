import decimal
import json, boto3
import os

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.getenv('TABLE_NAME', 'default-table-name')  # Default table name if not set

def _response(status_code, body_dict):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "PUT,POST,OPTIONS"
        },
        "body": json.dumps(body_dict)
    }

def lambda_handler(event, context):
    try:

        # 1. Extract path param and JSON body
        session_id = event["pathParameters"]["session_id"]
        body = json.loads(event.get("body", "{}"))

        # 2. Validate required fields
        required = ["title", "system_prompt", "model", "temperature"]
        missing = [f for f in required if f not in body]
        if missing:
            return _response(400, {
                "error": "Missing required fields",
                "missing": missing
            })

        # 3. Get the existing config from DynamoDB
        table = dynamodb.Table(TABLE_NAME)
        response = table.get_item(Key={"session_id": session_id})
        if 'Item' not in response:
            return _response(404, {"error": "Chat config not found"})

        existing_session = response['Item']

        # 4. Update the DynamoDB item
        new_session = {
            "session_id": session_id,
            "title": body["title"],
            "system_prompt": body["system_prompt"],
            "model": body["model"],
            "temperature": decimal.Decimal(str(body["temperature"])),
            "messages": existing_session.get("messages", []),
            "created_at": existing_session.get("created_at", None),
            "updated_at": existing_session.get("updated_at", None),
            'chat_config_id': existing_session.get('chat_config_id', None)
        }

        table.put_item(Item=new_session)

        # 5. Return the updated session
        print(f"🔹 Updated session: {new_session}")
        print("✅ Chat config updated successfully")

        configs = {
            "session_id": new_session["session_id"],
            "title": new_session["title"],
            "system_prompt": new_session["system_prompt"],
            "model": new_session["model"],
            "temperature": float(new_session["temperature"]),
        }

        return _response(200, {"message": "Chat config updated successfully", "session_configs": configs})

    except Exception as e:
        print(f"⚠️ Error: {str(e)}")
        return _response(500, {"error": "Internal server error", "message": str(e)})

