# AI Maker – Backend

**Live Demo:** [AI Maker Web App](https://main.d1qaw8kgznw7l8.amplifyapp.com/)

---

## 📌 Overview

AI Maker is a **personal project built for study purposes** to explore full-stack AI-powered chat applications.
The backend is **serverless**, designed with **AWS Lambda**, **Amazon DynamoDB**, and **Amazon S3**, and exposes a simple REST API for creating and interacting with custom AI chat agents.

The project allows users to:

* Create custom AI chat configurations (model, system prompt, temperature, title).
* Share chat configurations via a unique link.
* Create individual chat sessions from shared configs.
* Have stateful AI conversations where history is stored.
* Update chat session settings (when allowed).

---

## 🛠 AWS Services Used

| Service                | Purpose                                                                |
| ---------------------- | ---------------------------------------------------------------------- |
| **AWS Lambda**         | Hosts all backend logic for API endpoints.                             |
| **Amazon API Gateway** | Exposes REST API endpoints to the frontend with CORS enabled.          |
| **Amazon S3**          | Stores chat configuration JSON files, enabling shareable chat configs. |
| **Amazon DynamoDB**    | Stores chat sessions, including conversation history and metadata.     |
| **Amazon CloudWatch**  | Logging and debugging backend Lambda executions.                       |
| **AWS Amplify**        | Hosts and deploys the frontend (React).                                |

---

## 📡 API Architecture

The backend exposes the following endpoints (base path:
`https://o4fjb5rine.execute-api.us-east-1.amazonaws.com/api`):

| Method   | Endpoint                        | Description                                                                                                           |
| -------- | ------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| **POST** | `/create-chat`                  | Stores a new chat configuration in S3 and returns a unique `chatConfigId`.                                            |
| **GET**  | `/chat-config/{chat_config_id}` | Loads a chat configuration from S3 by ID.                                                                             |
| **PUT**  | `/chat-config/{chat_config_id}` | Updates an existing chat configuration in S3. *(Optional, restricted in shared mode)*                                 |
| **POST** | `/chat-session`                 | Creates a new chat session in DynamoDB linked to a chat configuration.                                                |
| **POST** | `/session-message`              | Appends a user message to a session, sends context to Gemini API, stores AI reply in DynamoDB, and returns the reply. |
| **PUT**  | `/session/{session_id}`         | Updates session settings (model, prompt, temperature, title) in DynamoDB.                                             |

---

## 🗂 Data Storage Design

### **Amazon S3 – Chat Configurations**

* **Key:** `chatConfigId.json`
* **Example Object:**

```json
{
  "chatConfigId": "123e4567-e89b-12d3-a456-426614174000",
  "model": "gemini-2.5-flash",
  "systemPrompt": "You are a helpful assistant.",
  "temperature": 0.7,
  "title": "Travel Buddy"
}
```

### **Amazon DynamoDB – Chat Sessions**

* **Partition Key:** `session_id` (string, UUID)
* **Attributes:**

  * `chat_config_id`
  * `title`
  * `system_prompt`
  * `model`
  * `temperature`
  * `messages` (array of `{role, content}`)
  * `created_at`
  * `updated_at`

---

## 🤖 AI Model Integration

* Uses **Google Gemini API** (e.g., `gemini-2.0-flash`, `gemini-2.5-flash`, `gemini-2.5-flash-lite`).
* The model choice, system prompt, and temperature are stored in the chat config and session.
* AI responses are **stateful**, preserving chat history in DynamoDB.

---

## 🔄 Typical Flow

1. **User creates a chat config** → stored in **S3** → returns shareable URL.
2. **Friend opens link** → backend loads config → creates a **new chat session** in DynamoDB.
3. **User sends messages** → backend retrieves history → sends to **Gemini API** → saves reply to DynamoDB → returns reply to frontend.
4. **(Optional)** Session owner can update settings using the `/session/{session_id}` endpoint.

---

## 🚀 Deployment

* **Backend:**

  * AWS Lambda functions deployed via AWS Console or ZIP uploads.
  * API Gateway routes map to Lambda handlers.
* **Frontend:**

  * React app deployed on AWS Amplify → [AI Maker Web App](https://main.d1qaw8kgznw7l8.amplifyapp.com/)

---

## 📖 Project Status

✅ Functional for study and demonstration purposes.
⚠ Not intended for production use without security hardening, authentication, and usage quotas.

---

## 📜 License

This project is created for **educational purposes only**.
No license for commercial use.

---

**Author:** Matan Moskowitz
**Contact:** via [GitHub](https://github.com/mosmatan) | [LinkedIn](https://www.linkedin.com/in/matan-moskovich/)
