
import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from groq import Groq

# Add phase 3 to path
phase_3_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "phase_3_retrieval"))
sys.path.append(phase_3_dir)

from retrieval_engine import RetrievalEngine

# Load environment
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", "phase_4_llm", ".env"))

app = FastAPI(title="NextLeap Chatbot API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize retrieval engine and Groq client
retrieval_engine = None
groq_client = None

@app.on_event("startup")
async def startup_event():
    global retrieval_engine, groq_client
    print("Initializing Retrieval Engine...")
    retrieval_engine = RetrievalEngine()
    
    api_key = os.getenv("GROQ_API_KEY")
    if api_key and "your_groq_api_key_here" not in api_key:
        groq_client = Groq(api_key=api_key)
        print("Groq Client initialized.")
    else:
        print("Warning: GROQ_API_KEY not set. LLM features disabled.")

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not retrieval_engine:
        raise HTTPException(status_code=500, detail="Retrieval engine not initialized")
    
    query = request.message.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    # Retrieve context
    context_str = retrieval_engine.retrieve_context(query, k=5)
    
    if not groq_client:
        return ChatResponse(response=f"Retrieval only (LLM not configured):\n{context_str}")
    
    # Generate response
    system_prompt = """You are a friendly and knowledgeable assistant for NextLeap, an ed-tech platform that helps people transition into Product Management, UI/UX Design, Data Analytics, and other tech roles.

Your personality:
- Warm and approachable, like a helpful friend who's excited to share what they know
- Professional but conversational - avoid being overly formal or robotic
- Encouraging and supportive, especially when discussing career transitions
- Clear and concise in your explanations

Instructions:
1.  You have multiple Context sources from NextLeap's course catalog.
    - If the user asks about a SPECIFIC course (e.g., "Product Management"), focus only on that course's context.
    - If the user asks a GENERAL question (e.g., "What courses do you offer?"), summarize from all relevant contexts.
2.  If the retrieved context has info for multiple courses and the user's question is ambiguous, briefly clarify which course you're referring to or list options.
3.  If the answer isn't in the context, say something like: "I don't have that specific information in my knowledge base right now. Could you ask about something else, or would you like to know more about [related topic]?"
4.  Use a friendly, conversational tone:
    - ✅ "Great question! The PM Fellowship runs for 16 weeks..."
    - ✅ "You'll learn tools like Figma, SQL, and JIRA..."
    - ❌ "The duration of the course is 16 weeks." (too formal)
5.  Be concise but helpful - don't overwhelm with too much info at once.
"""
    
    user_message = f"""Context:
{context_str}

User Question: {query}
"""
    
    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.1,
            max_tokens=1024,
        )
        response_text = chat_completion.choices[0].message.content
        return ChatResponse(response=response_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")

@app.get("/health")
async def health():
    return {"status": "ok", "llm_enabled": groq_client is not None}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
