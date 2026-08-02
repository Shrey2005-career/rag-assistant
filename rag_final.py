from sentence_transformers import SentenceTransformer
import chromadb
import google.generativeai as genai
import os
from dotenv import load_dotenv

# --- Load env variables ----
load_dotenv()

# ---- initialize models ----
print("\nInitializing Models...")
genai.configure(api_key=os.environ.get("GEMINI_API"))

gemini = genai.GenerativeModel(
    model_name="gemini-2.5-flash-lite",
    generation_config={
        "temperature": 0.2,
        "top_p": 0.95,
        "max_output_tokens": 1024
    }
)

# ---- embedding model ----
print("\nInitialzing the embeddings model...")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# ---- initialize chromadb ----
client = chromadb.Client()
collection = client.create_collection(name="final_rag_knowledgebase")



# ---- Get the knowledge from the file:
with open("knowledge.txt", "r") as f:
    knowledge = f.read()
    print(type (knowledge))
    
# ---- chunker ----
def chunk(text, chunk_size=80, overlap=10):
    chunks = []
    words = text.split()
    start = 0
    
    while(start < len(words)):
        end = start + chunk_size
        piece = ' '.join(words[start:end])
        chunks.append(piece)
        start += chunk_size - overlap
    return chunks


# ---- chunk the knowledge and create the documents from it:
documents = chunk(knowledge, chunk_size=100, overlap=20)

# ---- embed the documents ----
embedded_chunk = embedding_model.encode(documents).tolist()

# ---- add the embedded chunk with original documents in chromaDB:
collection.add(
    documents=documents,
    embeddings=embedded_chunk,
    ids=[f"doc_{i}" for i in range(len(documents))]
)

print(f"Stored {collection.count()} documents in vector database")

# Rewrite the messy queries

def rewrite_query(question):
    prompt = f"""You are a search query optimizer. 
Rewrite the following user question into a clear, specific search query 
that will retrieve the most relevant information from a knowledge base.

Rules:
- Make it specific and informative
- Remove casual language, typos, slang
- Keep it as one sentence
- Do NOT answer the question, just rewrite it

User question: {question}
Optimized search query:"""

    response = gemini.generate_content(prompt)
    return response.text.strip()


def rerank_chunks(question, chunks):
    """
    Ask Gemini to score each chunk's relevance to the question.
    Returns chunks sorted by relevance score, highest first.
    """
    scored_chunks = []

    for chunk in chunks:
        prompt = f"""Rate how relevant this text is for answering the question.
        
Question: {question}
Text: {chunk}

Reply with ONLY a number from 0 to 10.
0 = completely irrelevant
10 = directly answers the question

Score:"""

        response = gemini.generate_content(prompt)
        
        # Extract the number from response
        try:
            score = float(response.text.strip())
        except:
            score = 0  # if parsing fails, treat as irrelevant
            
        scored_chunks.append((score, chunk))
        
    # Sort by score, highest first
    scored_chunks.sort(reverse=True)
    
    # Return just the chunks, without scores
    return [chunk for score, chunk in scored_chunks]

def ask(question):
        # Step 1: Rewrite the query first
    optimized_query = rewrite_query(question)
    print(f"  [Optimized query: {optimized_query}]")
    
    # Step 2: Embed the OPTIMIZED query, not the original
    quest = embedding_model.encode([optimized_query]).tolist()
    
    # Step 3: Retrive
    results = collection.query(
        query_embeddings=quest,
        n_results=5
    )
    
    retrieved_chunks = results['documents'][0]
    
    # Step 4: Re-rank and keep top 3
    reranked_chunks = rerank_chunks(question, retrieved_chunks)
    top_chunks = reranked_chunks[:3] 
 
    
    
    # Step 5: Build prompt with ORIGINAL question but retrieved contex
    context = "\n".join(top_chunks)
    # Prepare the promt:
    prompt = f"""You are a smart, friendly assistant for this app.

    RULES:
    1. Answer using ONLY the context provided below.
    2. If the answer is not in the context, say: "I don't have enough information about that. Feel free to ask anything about this app or service!"
    3. If the user is trolling or using casual insults (e.g. "you're dumb", "ur stupid"):
    - Respond warmly and with light humor
    - Ask if something frustrated them or if they'd like to share feedback
    - Invite them to ask a real question

    Context:
    {context}

    Question: {question}
    Answer:"""
    
    # --- Now get the answer ----
    response = gemini.generate_content(prompt)
    
    return {
        "answer": response.text,
        "before_sources": retrieved_chunks,
        "after_re-ranking_sources": top_chunks,
        "optimized_query": optimized_query
    }
    

questions = [
    "How does RAG reduce hallucination?",
    "What is the difference between deep learning and machine learning?",
    "What techniques are used in prompt engineering?"
]

messy_questions = [
    "whats that thing about getting info from outside docs?",
    "lol how does the vector thingy work bro",
    "tell me abt embeddings",
    "how does rag not make stuff up?",
    "ur so dumb lol",                          # troll
    "who made this app???"                     # off topic
]

# Pass one question at a time:
for question in questions:
    print(f"Q: {question}")
    result = ask(question)
    print(f"A: {result['answer']}")
    print(f"\nSources used:")
    for i, source in enumerate(result['after_re-ranking_sources']):
        print(f"  {i+1}. {source}")
    print("\n" + "="*60 + "\n")