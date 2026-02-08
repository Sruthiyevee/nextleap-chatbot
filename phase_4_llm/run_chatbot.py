
import os
import sys
import argparse
from dotenv import load_dotenv
from groq import Groq
from termcolor import colored

# Add phase 3 directory to system path
phase_3_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "phase_3_retrieval"))
sys.path.append(phase_3_dir)

try:
    from retrieval_engine import RetrievalEngine
except ImportError:
    print(colored("Error: Could not import RetrievalEngine from phase 3.", "red"))
    sys.exit(1)

# Load environment variables
load_dotenv()

class NextLeapChatbot:
    def __init__(self):
        print(colored("Initializing NextLeap Chatbot...", "cyan"))
        
        # Initialize Retrieval Engine
        try:
            self.retrieval_engine = RetrievalEngine()
        except Exception as e:
            print(colored(f"Error initializing Retrieval Engine: {e}", "red"))
            sys.exit(1)
            
        # Initialize Groq Client
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key or "your_groq_api_key_here" in api_key:
            print(colored("Error: GROQ_API_KEY not found or not set in .env file.", "red"))
            print("Please edit phase_4_llm/.env and add your API Key.")
            self.groq_client = None
        else:
            self.groq_client = Groq(api_key=api_key)
            print(colored("Groq Client initialized successfully.", "green"))

    def generate_response(self, query: str) -> str:
        """
        Retrieves context and generates an answer using Groq LLM.
        """
        # 1. Retrieve Context
        print(colored(f"\nRetrieving relevant context for: '{query}'...", "yellow"))
        # Increase k to 5 to catch relevant chunks even if not Top-1
        context_str = self.retrieval_engine.retrieve_context(query, k=5)
        
        if not self.groq_client:
            return f"I can only verify Retrieval (LLM not configured):\n{context_str}"

        # 2. Construct Prompt
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

        # 3. Call LLM
        print(colored("Generating answer with Groq (llama-3.3-70b-versatile)...", "green"))
        try:
            chat_completion = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.1, # Low temperature for factual accuracy
                max_tokens=1024,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            return f"Error generating answer: {e}"

def main():
    parser = argparse.ArgumentParser(description="Run the NextLeap Chatbot")
    parser.add_argument("--query", type=str, help="Single query to run and exit")
    args = parser.parse_args()

    chatbot = NextLeapChatbot()
    
    if args.query:
        response = chatbot.generate_response(args.query)
        print(f"\nNextLeap Bot: {response}\n")
        return

    print("\n" + "="*50)
    print("   NextLeap Intelligent Chatbot (RAG Powered)")
    print("="*50)
    print("Type 'exit' or 'quit' to end the session.\n")

    while True:
        try:
            user_input = input(colored("You: ", "blue"))
            if user_input.lower() in ['exit', 'quit']:
                print("Goodbye!")
                break
            
            if not user_input.strip():
                continue
                
            response = chatbot.generate_response(user_input)
            print(f"\n{colored('NextLeap Bot:', 'green')} {response}\n")
            print("-" * 50)
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
