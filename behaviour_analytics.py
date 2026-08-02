import pandas as pd
from datetime import datetime
from memory_manager import MemoryManager

class BehaviourAnalyzer:
    def __init__(self, memory: MemoryManager):
        self.memory = memory
        
    def _events_to_df(self):
        """Convert events list to a Pandas DataFrame."""
        events = self.memory.get_events()
        if not events:
            return pd.DataFrame()
        
        rows = []
        for event in events:
            row = {
                "timestamp": pd.to_datetime(event["timestamp"]),
                "action": event["action"],
            }
            # Flatten metadata into columns
            row.update(event.get("metadata", {}))
            rows.append(row)
        
        return pd.DataFrame(rows)
    
    def completion_rate(self):
        """What % of added tasks get completed?"""
        df = self._events_to_df()
        if df.empty:
            return 0.0
        
        added = len(df[df["action"] == "add_task"])
        completed = len(df[df["action"] == "complete_task"])
        
        if added == 0:
            return 0.0
        return round(completed / added * 100, 1)
    
    def priority_breakdown(self):
        """How does this user distribute task priorities?"""
        df = self._events_to_df()
        if df.empty or "priority" not in df.columns:
            return {}
        
        adds = df[df["action"] == "add_task"]
        counts = adds["priority"].value_counts()
        return counts.to_dict()
    
    def most_common_topics(self, top_n=3):
        """What words appear most in their tasks?"""
        df = self._events_to_df()
        if df.empty or "task" not in df.columns:
            return []
        
        adds = df[df["action"] == "add_task"]
        
        # Count word frequency across all tasks
        word_counts = {}
        stopwords = {"a", "an", "the", "to", "for", "and", "or", "my", "i"}
        
        for task in adds["task"].dropna():
            for word in task.lower().split():
                
                
                if word not in stopwords and len(word) > 2:
                    word_counts[word] = word_counts.get(word, 0) + 1
                    
         
            
        # Sort by frequency
        sorted_words = sorted(
            word_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_words[:top_n]
    
    def activity_by_hour(self):
        """When is this user most active?"""
        df = self._events_to_df()
        if df.empty:
            return {}
        


        df["hour"] = df["timestamp"].dt.hour
        hourly = df.groupby("hour").size()
        return hourly.to_dict()
    
    def generate_insight(self):
        """Summarize everything into a human readable insight."""
        rate = self.completion_rate()
        priorities = self.priority_breakdown()
        topics = self.most_common_topics()
        
        # Determine dominant priority
        dominant_priority = max(priorities, key=priorities.get) if priorities else "unknown"
        top_topics = [word for word, count in topics]
        
        insight = {
            "completion_rate": rate,
            "dominant_priority": dominant_priority,
            "top_topics": top_topics,
            "priority_breakdown": priorities,
        }
        return insight