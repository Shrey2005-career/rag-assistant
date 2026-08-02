import json
import os
from datetime import datetime

class MemoryManager:
    def __init__(self, user_id, storage_dir="user_data"):
        self.user_id = user_id
        self.storage_dir = storage_dir
        
        # Create storage directory if it doesn't exist
        os.makedirs(storage_dir, exist_ok=True)
        
        # Each user gets their own file
        self.filepath = f"{storage_dir}/{user_id}.json"
        
        # Load existing data or start fresh
        self.data = self._load()
    
    def _load(self):
        """Load user data from file."""
        if os.path.exists(self.filepath):
            with open(self.filepath, "r") as f:
                return json.load(f)
        # Fresh user — initialize empty structure
        return {
            "user_id": self.user_id,
            "conversations": [],
            "events": [],
            "profile": {}
        }
    
    def _save(self):
        """Save user data to file."""
        with open(self.filepath, "w") as f:
            json.dump(self.data, f, indent=4)
    
    def log_conversation(self, question, answer, session_id="default"):
        """Store a question-answer pair."""
        self.data["conversations"].append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "session_id": session_id,
            "question": question,
            "answer": answer
        })
        self._save()
    
    def log_event(self, action, metadata=None):
        """Store a user action/behaviour event."""
        self.data["events"].append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "action": action,
            "metadata": metadata or {}
        })
        self._save()
    
    def update_profile(self, key, value):
        """Store/update a user profile attribute."""
        self.data["profile"][key] = value
        self._save()
    
    def get_recent_conversations(self, n=5):
        """Get the last n conversations."""
        return self.data["conversations"][-n:]
    
    def get_events(self, action_filter=None):
        """Get all events, optionally filtered by action type."""
        if action_filter:
            return [e for e in self.data["events"] 
                   if e["action"] == action_filter]
        return self.data["events"]
    
    def get_profile(self):
        return self.data["profile"]
    
    def summary(self):
        """Quick overview of what we know about this user."""
        total_convos = len(self.data["conversations"])
        total_events = len(self.data["events"])
        profile = self.data["profile"]
        
        print(f"\n--- Memory Summary for {self.user_id} ---")
        print(f"Total conversations: {total_convos}")
        print(f"Total events logged: {total_events}")
        print(f"Profile: {profile}")    