import json
import boto3
import os
import google.generativeai as genai
from datetime import datetime
from model import chat_from_dict, chat_to_dict, Message

dynamodb = boto3.resource("dynamodb")

SESSION_TABLE_NAME = os.getenv("SESSION_TABLE_NAME", 'your-chat-table-name')

def _respond(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(body)
    }

def _generate_response(session):
    print(f"Generating response for session_id {session.session_id}")

    # Load Gemini API
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel(model_name=session.model)

    # Prepare messages
    history = session.messages[-4:]
    history = [
        {"role": "user", "parts": [f'This is your system prompt: {session.system_prompt}.\nYou should act as the system prompt say and answer only to prompts that related to the system prompt. The next message are our chat history. Please respond to the last message in the chat history.']},
    ] + [{"role": m.role, "parts": [m.content]} for m in history]

    print(f"Chat history for session {session.session_id}: {history}")
    print(f'Using model: {session.model} with temperature: {session.temperature}')

    # Generate content
    response = model.generate_content(
        contents=history,
        generation_config={
            "temperature": session.temperature,
            "max_output_tokens": 1024
        }
    )
    assistant_msg = response.text

    # Append AI response
    session.messages.append(Message(role="model", content=assistant_msg))
    session.updated_at = datetime.utcnow()

    return assistant_msg


def lambda_handler(event, context):
    try:
        body = json.loads(event["body"])
        session_id = body.get("session_id")
        message = body.get("message")

        if not session_id or not message:
            print('Missing required fields: session_id or message')
            return _respond(400, {"error": "session_id and message are required"})

            # Retrieve session from DynamoDB
        print(f"Retrieving session with session_id {session_id} from DynamoDB")
        table = dynamodb.Table(SESSION_TABLE_NAME)
        response = table.get_item(Key={"session_id": session_id})
        item = response.get("Item")
        if not item:
            print(f"Chat with session_id {session_id} not found")
            return _respond(404, {"error": "Chat not found"})

        session = chat_from_dict(item)
        print(f"Retrieved chat: {session.session_id}")

        session.messages.append(Message(role="user", content=message))
        assistant_msg = _generate_response(session)

        # Save the updated chat back to DynamoDB
        print(f"Saving updated chat with session_id {session.session_id} to DynamoDB")

        table.put_item(Item=chat_to_dict(session))
        print(f"Chat {session.session_id} updated successfully")

        return _respond(200, {"message": assistant_msg})

    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return _respond(500, {"error": "Internal server error"})




