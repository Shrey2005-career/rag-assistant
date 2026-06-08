import google.generativeai as genai
from sentence_transformers import SentenceTransformer
import chromadb
import os
from dotenv import load_dotenv
from memory_manager import MemoryManager
from behaviour_analytics import BehaviourAnalyzer

load_dotenv()
genai.configure(api_key=os.environ.get("GEMINI_API"))

gemini = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    generation_config={"temperature": 0.4, "max_output_tokens": 1024}
)

embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# ---- Setup ChromaDB with knowledge ----
client = chromadb.Client()
collection = client.create_collection("personalised_rag")

knowledge = [
    "You can add tasks by clicking the + button or typing in the input field.",
    "Tasks can be set to High, Medium or Low priority.",
    "You can set deadlines by clicking the calendar icon on any task.",
    "Completed tasks are moved to the Done section automatically.",
    "You can filter tasks by priority, deadline, or category.",
    "The app sends reminders 1 hour before task deadlines.",
    "You can create recurring tasks that repeat daily, weekly or monthly.",
    "The productivity score is calculated based on your completion rate.",
    "You can share tasks with team members by clicking the share icon.",
    "The app supports dark mode which can be toggled in settings.",
]

embeddings = embedding_model.encode(knowledge).tolist()
collection.add(
    documents=knowledge,
    embeddings=embeddings,
    ids=[f"doc_{i}" for i in range(len(knowledge))]
)


# ---- Build user context from memory + analytics ----
def build_user_context(memory: MemoryManager):
    analyzer = BehaviourAnalyzer(memory)
    insight = analyzer.generate_insight()
    profile = memory.get_profile()
    recent_convos = memory.get_recent_conversations(3)

    # Format recent conversations
    convo_text = ""
    if recent_convos:
        convo_text = "\n".join([
            f"- They asked: '{c['question']}'"
            for c in recent_convos
        ])

    # Build a natural language summary of the user
    user_context = f"""
USER PROFILE:
- Name: {profile.get('name', 'User')}
- Completion rate: {insight['completion_rate']}%
- Dominant priority style: {insight['dominant_priority']}
- Topics they care about: {', '.join(insight['top_topics'])}
- Priority breakdown: {insight['priority_breakdown']}

RECENT CONVERSATIONS:
{convo_text if convo_text else "No previous conversations."}
"""
    return user_context, insight


# ---- Predict what user might need next ----
def predict_next_action(insight):
    rate = insight['completion_rate']
    dominant = insight['dominant_priority']
    topics = insight['top_topics']

    suggestions = []

    if rate < 40:
        suggestions.append(
            "consider breaking down your high-priority tasks into smaller steps"
        )
    elif rate > 75:
        suggestions.append(
            "set more challenging goals since you're completing tasks efficiently"
        )

    if dominant == "high":
        suggestions.append(
            "review your high-priority items first thing each morning"
        )

    if topics:
        suggestions.append(
            f"create a dedicated category for '{topics[0]}' tasks since you focus on them often"
        )

    return suggestions


# ---- Personalised ask function ----
def ask(user_id, question):
    # Load user memory
    memory = MemoryManager(user_id)
    user_context, insight = build_user_context(memory)
    predictions = predict_next_action(insight)

    # Retrieve relevant knowledge
    query_embedding = embedding_model.encode([question]).tolist()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=3
    )
    retrieved_chunks = results['documents'][0]
    knowledge_context = "\n".join(retrieved_chunks)

    # Build personalised prompt
    predictions_text = "\n".join([f"- {s}" for s in predictions]) \
        if predictions else "None"

    prompt = f"""You are a smart, personalised assistant for a To-Do app.
You know this specific user well. Use their profile to personalise your response.

{user_context}

APP KNOWLEDGE:
{knowledge_context}

PREDICTED NEEDS (optionally weave into your response if relevant):
{predictions_text}

RULES:
1. Address the user by name if you know it
2. Tailor your response to their productivity style
3. Answer using the app knowledge above
4. If completion rate is low, be encouraging
5. If completion rate is high, be affirming
6. Keep responses concise and friendly

Question: {question}
Answer:"""

    response = gemini.generate_content(prompt)

    # Log this conversation to memory
    memory.log_conversation(question, response.text)

    return {
        "answer": response.text,
        "user_context": user_context,
        "predictions": predictions,
        "sources": retrieved_chunks
    }


# ---- Test it ----
questions = [
    "How do I set a deadline for a task?",
    "Can I get reminders for my tasks?",
    "How can I be more productive?",
]

print("=" * 60)
print("PERSONALISED RAG DEMO")
print("=" * 60)

for question in questions:
    print(f"\nQ: {question}")
    result = ask("aryan_01", question)
    print(f"A: {result['answer']}")
    print(f"\nPredictions injected: {result['predictions']}")
    print("-" * 60)


# What Makes This Different From Basic RAG

# Basic RAG prompt:

# Answer this question using the context.
# Question: How do I set a deadline?


# Personalised RAG prompt:

# You know this user:
# - Name: Aryan
# - Completion rate: 44%
# - Focuses on: buy, finish, rag tasks
# - Recently asked about: adding tasks, priorities

# Answer this question for THIS specific user.
# Question: How do I set a deadline?