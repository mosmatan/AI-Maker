import os
import json
import boto3

# S3 client and bucket name (same env var you already use)
s3 = boto3.client('s3')
BUCKET = os.getenv('BUCKET_NAME', 'my-default-bucket')  # Default bucket name if not set

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
    print("🔹 Start update-config lambda")

    try:
        # 1. Extract path param and JSON body
        print("🔸 Extracting pathParameters and body")
        chat_config_id = event["pathParameters"]["chat_config_id"]
        body = json.loads(event.get("body", "{}"))
        print(f"🔹 Received update for config_id={chat_config_id} with body={body}")

        # 2. Validate required fields
        print("🔸 Validating required fields")
        required = ["title", "systemPrompt", "model", "temperature"]
        missing = [f for f in required if f not in body]
        if missing:
            print(f"⚠️ Missing fields: {missing}")
            return _response(400, {
                "error": "Missing required fields",
                "missing": missing
            })
        print("✅ Validation passed")

        # 3. Build the updated config object (camelCase keys)
        print("🔸 Building new config object")
        new_config = {
            "chatConfigId": chat_config_id,
            "title":        body["title"],
            "systemPrompt": body["systemPrompt"],
            "model":        body["model"],
            "temperature":  body["temperature"]
        }
        print(f"🔹 New config: {new_config}")

        # 4. Overwrite the existing S3 object
        print("🔸 Overwriting S3 object")
        s3.put_object(
            Bucket=BUCKET,
            Key=f'chat-configs/{chat_config_id}.json',
            Body=json.dumps(new_config)
        )
        print("✅ S3 object overwritten successfully")

        # 5. Return the new config
        print("🔸 Returning success response")
        return _response(200, new_config)

    except Exception as e:
        print("❌ Error in update-config:", e)
        return _response(500, {"error": str(e)})
