import os
from dotenv import load_dotenv
from google import genai
from pinecone import Pinecone

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX = os.getenv("PINECONE_INDEX", "harrier-rag")

client = genai.Client(api_key=GEMINI_API_KEY)
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX)


def retrieve_context(query: str, top_k: int = 5) -> str:
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=query
    )

    query_embedding = result.embeddings[0].values

    response = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True
    )

    matches = response.get("matches", [])
    contexts = [
        match["metadata"]["text"]
        for match in matches
        if "metadata" in match and "text" in match["metadata"]
    ]

    return "\n\n".join(contexts)


def stream_answer(query: str):
    context = retrieve_context(query)

    if not context.strip():
        yield "The answer is not available in the knowledge base."
        return

    prompt = f"""
You are a secure classroom demo assistant.

STRICT RULES:
- Answer ONLY from the provided context.
- If not found in context, say: "The answer is not available in the knowledge base."
- Do not guess.
- Do not fabricate information.

Context:
{context}

Question:
{query}
"""

    response = client.models.generate_content_stream(
        model="gemini-2.5-flash",
        contents=prompt
    )

    for chunk in response:
        if chunk.text:
            yield chunk.text