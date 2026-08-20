# Personalized RAG Assistant

A Python-based AI assistant that uses **Retrieval-Augmented Generation**, **user memory**, and **behaviour analytics** to provide more relevant and personalized answers.

This project demonstrates how a chatbot can be improved by combining document retrieval, vector search, user history, and behavioural insights. Instead of giving the same generic response to every user, the assistant retrieves useful information from a knowledge base and adapts its response based on the user's stored profile, past conversations, and task activity.

---

## Project Overview

Many basic AI assistants answer questions only from the model's general knowledge. This can lead to generic answers and sometimes incorrect responses. This project uses a Retrieval-Augmented Generation pipeline to ground answers in a custom knowledge base.

The project also adds a personalization layer. It stores user interactions, analyzes task behaviour, and uses those insights to make responses more specific to the user.

The system focuses on three main goals:

1. Retrieve relevant information from a custom knowledge base.
2. Improve answer quality using query rewriting and re-ranking.
3. Personalize responses using user memory and behaviour analytics.


## Key Features

### Retrieval-Augmented Generation

The assistant retrieves relevant information from a custom knowledge base before generating an answer. This helps the response stay grounded in the available context.

### Query Rewriting

User questions may be casual, unclear, or contain spelling mistakes. The system rewrites the original question into a clearer search query before retrieving information.

Example:

```text
User Question:
how does rag not make stuff up?

Optimized Query:
How does retrieval augmented generation reduce hallucination in AI responses?
```

### Semantic Search

The project uses sentence embeddings to search for meaning instead of only matching exact words. This allows the assistant to find relevant information even when the user's question is phrased differently from the knowledge base.

### Vector Database

ChromaDB is used to store embedded knowledge chunks and retrieve the most relevant chunks based on the user's question.

### LLM-Based Re-Ranking

The first retrieval step may return chunks that are only partially useful. To improve the final context, the retrieved chunks are scored and re-ranked based on their relevance to the original question.

### User Memory

The project includes a memory manager that stores user-specific data in JSON format.

It stores:

* User profile information
* Previous conversations
* User actions
* Task activity
* Session-based question-answer history

### Behaviour Analytics

The behaviour analytics module analyzes user task activity and generates useful insights.

It calculates:

* Task completion rate
* Priority distribution
* Most common task topics
* User activity by hour
* Dominant priority style

### Personalized Responses

The personalized assistant uses retrieved knowledge, user memory, and behaviour insights together to generate responses that are more relevant to the specific user.

---

## Tech Stack

| Category              | Technology            |
| --------------------- | --------------------- |
| Programming Language  | Python                |
| Large Language Model  | Google Gemini         |
| Embedding Model       | all-MiniLM-L6-v2      |
| Embedding Library     | Sentence Transformers |
| Vector Database       | ChromaDB              |
| Data Analysis         | Pandas                |
| Storage               | JSON                  |
| Environment Variables | python-dotenv         |

---

## Project Structure

```text
.
├── rag_final.py
├── personalised_rag.py
├── memory_manager.py
├── behaviour_analytics.py
├── knowledge.txt
├── aryan_01.json
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## File Description

| File                     | Description                                                                                  |
| ------------------------ | -------------------------------------------------------------------------------------------- |
| `rag_final.py`           | Main RAG pipeline with query rewriting, semantic search, re-ranking, and response generation |
| `personalised_rag.py`    | Personalized RAG assistant that uses memory and behaviour analytics                          |
| `memory_manager.py`      | Handles user profile, conversations, events, and local JSON storage                          |
| `behaviour_analytics.py` | Analyzes task completion rate, priorities, common topics, and activity patterns              |
| `knowledge.txt`          | Custom knowledge base used for retrieval                                                     |
| `aryan_01.json`          | Sample user data used for testing personalization                                            |
| `requirements.txt`       | Python dependencies required to run the project                                              |
| `.env.example`           | Example environment file showing required API key format                                     |
| `.gitignore`             | Files and folders that should not be pushed to GitHub                                        |

---

## How It Works

### 1. Load the Knowledge Base

The system reads information from `knowledge.txt`. The knowledge base contains AI/ML-related information such as artificial intelligence, machine learning, deep learning, NLP, large language models, RAG, vector embeddings, and prompt engineering.

### 2. Split Text into Chunks

The knowledge base is divided into smaller overlapping chunks. This improves retrieval because the system can search focused sections of text instead of one large document.

### 3. Generate Embeddings

Each text chunk is converted into a vector embedding using the Sentence Transformer model.

```python
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
```

### 4. Store Embeddings in ChromaDB

The text chunks and their embeddings are stored in a ChromaDB collection. This allows the system to perform semantic search.

### 5. Rewrite the User Query

Before searching the vector database, the user's question is rewritten into a clearer query. This improves retrieval when the original question is informal or unclear.

### 6. Retrieve Relevant Chunks

The optimized query is embedded and searched against the ChromaDB collection. The system retrieves the most relevant chunks from the knowledge base.

### 7. Re-Rank the Retrieved Chunks

The retrieved chunks are scored based on how useful they are for answering the original question. The top-ranked chunks are selected as final context.

### 8. Generate the Final Answer

The final answer is generated using the selected context and the original user question.

### 9. Add Personalization

In the personalized version, the assistant also uses user memory and behaviour insights. This allows it to answer based on both the retrieved knowledge and the user's previous activity.

---

## Example Questions

```text
How does RAG reduce hallucination?
What is the difference between deep learning and machine learning?
What techniques are used in prompt engineering?
How do I set a deadline for a task?
Can I get reminders for my tasks?
How can I be more productive?
```

---

## Sample Output

```text
Q: How does RAG reduce hallucination?

Optimized Query:
How does retrieval augmented generation reduce hallucination in AI responses?

A:
Retrieval-Augmented Generation reduces hallucination by retrieving relevant documents from a knowledge base and using them as grounding context for the language model. This helps the model generate answers based on factual information instead of relying only on its internal knowledge.
```

---

## Personalization Example

The assistant can use stored user data to personalize responses.

Example user insights:

```text
Name: Aryan
Completion Rate: 44.4%
Dominant Priority Style: High
Top Topics: buy, finish, rag
```

Using these insights, the assistant can give responses that match the user's task behaviour, such as suggesting better ways to manage high-priority tasks or organize frequently repeated topics.

## What Makes This Project Different

This project is more than a basic RAG chatbot because it combines retrieval with user-specific context.

It includes:

* Query rewriting before retrieval
* Semantic search using embeddings
* ChromaDB-based vector storage
* LLM-based re-ranking
* JSON-based user memory
* Behaviour analytics
* Personalized response generation

These features make the assistant more practical and closer to real-world AI assistant systems.

---

## What I Learned

Through this project, I learned how to:

* Build a RAG pipeline using Python
* Use Sentence Transformers for embeddings
* Store and search vectors using ChromaDB
* Improve retrieval using query rewriting
* Improve context quality using re-ranking
* Integrate Gemini into a Python application
* Store user-specific memory using JSON
* Analyze user behaviour using Pandas
* Generate personalized AI responses using memory and analytics

---

## Author

Developed as an AI/ML project to demonstrate practical understanding of Retrieval-Augmented Generation, vector databases, LLM integration, user memory, and behaviour-based personalization.
