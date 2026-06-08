from memory_manager import MemoryManager
from behaviour_analytics import BehaviourAnalyzer

# Simulate Aryan using the app
aryan = MemoryManager("aryan_01")

# Simulate some conversations
aryan.log_conversation(
    question="How do I add a task?",
    answer="Click the + button to add a new task.",
    session_id="sess_001"
)
aryan.log_conversation(
    question="Can I set priorities?",
    answer="Yes, you can set High, Medium or Low priority.",
    session_id="sess_001"
)

# Simulate some behaviour events
aryan.log_event("add_task", {"task": "Buy groceries", "priority": "high"})
aryan.log_event("add_task", {"task": "Finish RAG project", "priority": "high"})
aryan.log_event("complete_task", {"task": "Buy groceries"})
aryan.log_event("add_task", {"task": "Call mom", "priority": "low"})
aryan.log_event("add_task", {"task": "Exercise", "priority": "medium"})
# Add more events to make analytics interesting
aryan.log_event("add_task", {"task": "Buy vegetables", "priority": "high"})
aryan.log_event("add_task", {"task": "Read ML paper", "priority": "medium"})
aryan.log_event("add_task", {"task": "Finish RAG lesson", "priority": "high"})
aryan.log_event("complete_task", {"task": "Finish RAG project"})
aryan.log_event("complete_task", {"task": "Finish RAG lesson"})
aryan.log_event("add_task", {"task": "Buy milk", "priority": "low"})
aryan.log_event("add_task", {"task": "Study embeddings", "priority": "medium"})
aryan.log_event("complete_task", {"task": "Call mom"})

# Update profile
aryan.update_profile("name", "Aryan")
aryan.update_profile("preferred_language", "English")

# Print summary
aryan.summary()

# Get recent conversations
print("\nRecent conversations:")
for convo in aryan.get_recent_conversations(2):
    print(f"  Q: {convo['question']}")
    print(f"  A: {convo['answer']}")

# Get specific events
print("\nAll add_task events:")
for event in aryan.get_events("add_task"):
    print(f"  {event['metadata']['task']} ({event['metadata']['priority']})")
    
    # Run analytics
analyzer = BehaviourAnalyzer(aryan)

print(f"Completion rate: {analyzer.completion_rate()}%")
print(f"Priority breakdown: {analyzer.priority_breakdown()}")
print(f"Most common topics: {analyzer.most_common_topics()}")
print(f"Activity by hour: {analyzer.activity_by_hour()}")

print("\n--- Full Insight ---")
insight = analyzer.generate_insight()
for key, value in insight.items():
    print(f"{key}: {value}")