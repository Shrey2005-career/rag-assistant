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
                
                # len(word) > 2 removes very short words that slipped 
                # through stopwords — like "my", "or", "is" that aren't 
                # in the stopwords set but are still meaningless for topic analysis.
                
                #"Buy groceries" → ["buy", "groceries"] ✅
                # "Call mom"      → ["call", "mom"]      ✅
                # "a", "an", "the", "to" → skipped      ❌
                
                if word not in stopwords and len(word) > 2:
                    word_counts[word] = word_counts.get(word, 0) + 1
                    
                    # If you just do this:
                    # word_counts["buy"] += 1   # crashes if "buy" doesn't exist yet!

                    # # So instead:
                    # word_counts["buy"] = word_counts.get("buy", 0) + 1
                    # "get me the current count, but if it doesn't exist yet, start from 0"
                    # then add 1 to whatever we got


                    # Step by step for "buy" appearing 3 times:

                    # First time:  word_counts.get("buy", 0) + 1 = 0 + 1 = 1
                    # Second time: word_counts.get("buy", 0) + 1 = 1 + 1 = 2
                    # Third time:  word_counts.get("buy", 0) + 1 = 2 + 1 = 3
        
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
        
        
# df["timestamp"].dt.hour    # → hour (0-23)
# df["timestamp"].dt.day     # → day of month
# df["timestamp"].dt.weekday # → 0=Monday, 6=Sunday
# df["timestamp"].dt.month   # → month number

# You first converted timestamps to datetime with pd.to_datetime() in _events_to_df() — that's what activates the .dt accessor. Without that conversion it's just a plain string and .dt wouldn't work.

# groupby("hour").size() → .to_dict()
# groupby groups all rows that share the same value, size() counts rows per group:
# pythondf["hour"]
# 18, 18, 18, 18, 18 ...  (all at hour 18 in your case)

# df.groupby("hour").size()
# hour
# 18    13
# dtype: int64

# Again this is a Series with hour as the index. .to_dict() converts it:
# {18: 13}, e.g., group = people who work 18 hours, so 18 hours is the group with 13 value means 13 users belong to this set
# or group.

# If you had events at different hours it'd look like:
# python{9: 3, 14: 5, 18: 7, 21: 2}
# That tells you the user is most active at 6pm.


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
        
        #Here, first 'word' before 'for' keyword is the variable's name that will iterate in the loop.

        #top_topics = [word for word, count in topics]
        # topics is a list of tuples: [("buy", 3), ("finish", 2), ("rag", 2)]
        # This unpacks each tuple and keeps only the word, throwing away the count:
        # python["buy", "finish", "rag"]
        
        insight = {
            "completion_rate": rate,
            "dominant_priority": dominant_priority,
            "top_topics": top_topics,
            "priority_breakdown": priorities,
        }
        return insight