
import os
import sys
import json
import sqlite3
import numpy as np
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer

# Configuration
DB_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "knowledge_base.db"))
MODEL_NAME = "all-MiniLM-L6-v2"
TOP_K = 3

class RetrievalEngine:
    def __init__(self):
        print(f"Loading embedding model: {MODEL_NAME}...")
        self.embedder = SentenceTransformer(MODEL_NAME)
        
        print(f"Loading knowledge base from {DB_FILE}...")
        self.chunks = []
        self.embeddings = []
        self._load_db()

    def _load_db(self):
        if not os.path.exists(DB_FILE):
             print(f"Error: Database file {DB_FILE} not found.")
             return

        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            # Fetch all embeddings
            cursor.execute("SELECT id, content, metadata, embedding_vector FROM course_embeddings")
            rows = cursor.fetchall()
            
            for row in rows:
                chunk_id, content, metadata_json, vector_json = row
                
                # Parse JSON
                metadata = json.loads(metadata_json)
                vector = np.array(json.loads(vector_json), dtype=np.float32)
                
                self.chunks.append({
                    "id": chunk_id,
                    "content": content,
                    "metadata": metadata
                })
                self.embeddings.append(vector)
            
            # Convert to numpy matrix for fast calc
            if self.embeddings:
                self.embedding_matrix = np.vstack(self.embeddings)
                # Normalize for cosine similarity
                norm = np.linalg.norm(self.embedding_matrix, axis=1, keepdims=True)
                self.embedding_matrix = self.embedding_matrix / (norm + 1e-10) # Avoid div by zero
            else:
                self.embedding_matrix = np.array([])
            
            print(f"Loaded {len(self.chunks)} chunks.")
            conn.close()
            
        except Exception as e:
            print(f"Error loading database: {e}")

    def search(self, query: str, k: int = 1) -> List[Dict[str, Any]]:
        """
        Embeds the query and performs cosine similarity search against the knowledge base.
        Returns top k chunks with their scores.
        """
        if len(self.chunks) == 0:
            return []

        # Embed query
        query_embedding = self.embedder.encode([query])[0]
        
        # Normalize query
        norm_query = query_embedding / (np.linalg.norm(query_embedding) + 1e-10)
        
        # Cosine Similarity
        similarities = np.dot(self.embedding_matrix, norm_query)
        
        # Get top k indices
        top_k_indices = np.argsort(similarities)[::-1][:k]
        
        results = []
        for idx in top_k_indices:
            score = similarities[idx]
            chunk = self.chunks[idx]
            results.append({
                "score": float(score),
                "content": chunk["content"],
                "metadata": chunk["metadata"]
            })
            
        return results

    def retrieve_context(self, query: str, k: int = 1) -> str:
        """
        Orchestrates the search and formats the retrieved chunks into a readable string.
        Does NOT call an LLM.
        """
        results = self.search(query, k=k)
        
        if not results:
            return "No relevant information found within the knowledge base."
            
        formatted_output = f"Top {len(results)} Retrieval Results:\n"
        formatted_output += "=" * 40 + "\n"
        
        for i, res in enumerate(results):
            formatted_output += f"Result {i+1} (Score: {res['score']:.4f})\n"
            formatted_output += f"Source: {res['metadata'].get('type', 'Unknown')} - {res['metadata'].get('course', 'Unknown')}\n"
            formatted_output += "-" * 20 + "\n"
            formatted_output += f"{res['content']}\n"
            formatted_output += "=" * 40 + "\n"
            
        return formatted_output

def main():
    print("Initializing Retrieval Engine (Phase 3)...")
    engine = RetrievalEngine()
    
    print("\n--- NextLeap Retrieval System ---")
    print("Type 'exit' to quit.\n")
    
    while True:
        try:
            query = input("Enter search query: ")
            if query.lower() in ['exit', 'quit']:
                break
                
            if not query.strip():
                continue
                
            context = engine.retrieve_context(query)
            print(context)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
