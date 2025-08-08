import decimal
from datetime import datetime

class Message:
    def __init__(self, role, content):
        self.role = role
        self.content = content

class Chat:
    def __init__(self, session_id,system_prompt = "You are a helpful assistant.", model = 'gemini-2.5-flash-lite',
                 title = 'New Session', messages=None,
                 chat_config_id="default", created_at=None, updated_at=None, temperature=0.7):
        self.session_id = session_id
        self.messages = messages or []
        self.chat_config_id = chat_config_id
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or self.created_at
        self.title = title
        self.system_prompt = system_prompt
        self.temperature = float(temperature)
        self.model = model


def chat_from_dict(item: dict) -> Chat:
    return Chat(
        session_id=item.get("session_id"),
        messages=[Message(m["role"], m["content"]) for m in item.get("messages", [])],
        chat_config_id=item.get("chat_config_id", "default"),
        created_at=datetime.fromisoformat(item["created_at"]),
        updated_at=datetime.fromisoformat(item.get("updated_at", item["created_at"])),
        system_prompt=item.get("system_prompt", "You are a helpful assistant."),
        title=item.get("title", "New Session"),
        temperature=float(item.get("temperature", 0.7)),
        model=item.get("model", "gemini-2.5-flash-lite")
    )

def chat_to_dict(chat: Chat) -> dict:
    return {
        "session_id": chat.session_id,
        "messages": [{"role": m.role, "content": m.content} for m in chat.messages],
        "chat_config_id": chat.chat_config_id,
        "created_at": chat.created_at.isoformat(),
        "updated_at": chat.updated_at.isoformat(),
        "system_prompt": chat.system_prompt,
        "title": chat.title,
        "temperature": decimal.Decimal(str(chat.temperature)),
        "model": chat.model
    }
