import redis
import json
from typing import List, Dict, Any

class ChatHistoryManager:
    def __init__(self, host: str = 'localhost', port: int = 6380, db: int = 0):
        self.r = redis.Redis(host=host, port=port, db=db)

    def add_chat_history(self, chat_id: str, messages: List[Dict[str, Any]]) -> None:
        stored_chat_history = self.r.hget(chat_id, "chat_history")

        if stored_chat_history:
            chat_history = json.loads(stored_chat_history)
        else:
            chat_history = {"messages": []}

        chat_history["messages"].extend(messages)
        self.r.hset(chat_id, "chat_history", json.dumps(chat_history))
        
        # Set the expiration time to 5 minutes (300 seconds)
        # self.r.expire(chat_id, 300)  # 300 seconds = 5 minutes
        
    def delete_history(self, chat_id: str) -> bool:
        return self.r.hdel(chat_id, "chat_history") > 0

    def update_history(self, chat_id: str, messages: List[Dict[str, Any]]) -> None:
        chat_history = {"messages": messages}
        self.r.hset(chat_id, "chat_history", json.dumps(chat_history))

    def get_history(self, chat_id: str,limit=20):
        """Retrieve the chat history for a specific chat ID."""
        stored_chat_history = self.r.hget(chat_id, "chat_history")

        if stored_chat_history:
             history = json.loads(stored_chat_history)
             return history['messages'][:limit]
        else:
            return []
