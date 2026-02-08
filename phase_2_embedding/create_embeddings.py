
import json
import os
import numpy as np
from sentence_transformers import SentenceTransformer

# Configuration
DATA_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "phase_1_data_scraping", "final_courses_data.json"))
EMBEDDING_DIR = os.path.dirname(__file__)
CHUNKS_FILE = os.path.join(EMBEDDING_DIR, "chunks.json")
EMBEDDINGS_FILE = os.path.join(EMBEDDING_DIR, "embeddings.npy")
MODEL_NAME = "all-MiniLM-L6-v2"

class SimpleTextSplitter:
    def __init__(self, chunk_size=1000, chunk_overlap=200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text):
        if not text:
            return []
        
        chunks = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = min(start + self.chunk_size, text_len)
            
            # If we are not at the end of text, try to break at a newline or space
            if end < text_len:
                # Look back for a newline
                last_newline = text.rfind('\n', start, end)
                if last_newline != -1:
                    end = last_newline + 1
                else:
                    # Look back for a space
                    last_space = text.rfind(' ', start, end)
                    if last_space != -1:
                        end = last_space + 1
            
            # If after trying to split intelligently, we end up with empty or negative, force hard split
            if end <= start:
                end = min(start + self.chunk_size, text_len)
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Calculate next start
            next_start = end - self.chunk_overlap
            
            # Prevent infinite loop or getting stuck
            if next_start <= start:
                next_start = start + max(1, len(chunk) - self.chunk_overlap)
                if next_start <= start: # unlikely
                     next_start = end 
            
            # If we reached the end, break
            if end >= text_len:
                break
                
            start = next_start

        return chunks

def load_data():
    if not os.path.exists(DATA_FILE):
        print(f"Error: Data file not found at {DATA_FILE}")
        return {}
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_chunks(data):
    s = SimpleTextSplitter(chunk_size=1000, chunk_overlap=200)
    all_chunks = []
    
    # Check if 'courses' exists
    if not isinstance(data.get("courses"), list):
        print("Error: 'courses' key missing or not a list")
        return []

    for course in data.get("courses", []):
        course_name = course.get("course_name", "Unknown Course")
        course_url = course.get("course_url", "")
        
        # Process cohorts
        cohorts = course.get("cohorts", [])
        if not cohorts:
            # Fallback if no cohorts? Just process course level info if any?
            # Schema imposes cohorts.
            pass

        for cohort in cohorts:
            cohort_label = cohort.get("cohort_label", "")
            details = cohort.get("cohort_details", {})
            
            # 1. Course Overview & Logistics
            overview_lines = [f"Course: {course_name}"]
            if cohort_label:
                overview_lines.append(f"Cohort: {cohort_label}")
            
            if "live_class_duration" in details: overview_lines.append(f"Duration: {details['live_class_duration']}")
            if "fellowship_timeline" in details: overview_lines.append(f"Timeline: {details['fellowship_timeline']}")
            if "mentorship" in details: overview_lines.append(f"Mentorship: {details['mentorship']}")
            if "placement_support" in details: overview_lines.append(f"Placement Support: {details['placement_support']}")
            if "cost" in details:
                 cost = details['cost']
                 overview_lines.append(f"Cost: {cost.get('amount', '')} {cost.get('currency', '')}")
            
            overview_text = "\n".join(overview_lines)
            
            for chunk_text in s.split_text(overview_text):
                all_chunks.append({
                    "text": chunk_text,
                    "metadata": {"source": course_url, "course": course_name, "type": "overview"}
                })
            
            # 2. Week-wise Curriculum (Grouped)
            curriculum_lines = [f"Course: {course_name} - Curriculum"]
            for week in details.get("weekwise_course_details", []):
                week_num = week.get("week")
                topics = ", ".join(week.get("topics", []))
                outcomes = ", ".join(week.get("learning_outcomes", []))
                curriculum_lines.append(f"Week {week_num}: Topics: {topics}. Outcomes: {outcomes}.")
            
            curriculum_text = "\n".join(curriculum_lines)

            for chunk_text in s.split_text(curriculum_text):
                all_chunks.append({
                    "text": chunk_text,
                    "metadata": {"source": course_url, "course": course_name, "type": "curriculum"}
                })

            # 3. Reviews (Individual)
            for review in details.get("reviews", []):
                review_lines = [f"Course: {course_name} Review"]
                review_lines.append(f"Reviewer: {review.get('reviewer_name', 'Anonymous')}")
                review_lines.append(f"Rating: {review.get('rating', '')}")
                review_lines.append(f"Review: {review.get('review_text', '')}")
                review_text = "\n".join(review_lines)
                
                for chunk_text in s.split_text(review_text):
                    all_chunks.append({
                        "text": chunk_text,
                        "metadata": {"source": course_url, "course": course_name, "type": "review"}
                    })

            # 4. FAQs (Individual)
            for faq in details.get("frequently_asked_questions", []):
                faq_lines = [f"Course: {course_name} FAQ"]
                faq_lines.append(f"Q: {faq.get('question', '')}")
                faq_lines.append(f"A: {faq.get('answer', '')}")
                faq_text = "\n".join(faq_lines)
                
                for chunk_text in s.split_text(faq_text):
                    all_chunks.append({
                        "text": chunk_text,
                        "metadata": {"source": course_url, "course": course_name, "type": "faq"}
                    })
                
            # 5. Success Stories (Individual)
            for story in details.get("success_stories", []):
                story_lines = [f"Course: {course_name} Success Story"]
                story_lines.append(f"Name: {story.get('name', '')}")
                story_lines.append(f"Background: {story.get('background', '')}")
                story_lines.append(f"Outcome: {story.get('outcome', '')}")
                story_text = "\n".join(story_lines)
                
                for chunk_text in s.split_text(story_text):
                    all_chunks.append({
                        "text": chunk_text,
                        "metadata": {"source": course_url, "course": course_name, "type": "success_story"}
                    })
            
            # 6. Instructors (Grouped)
            instructors = details.get("instructors", [])
            if instructors:
                instructor_lines = [f"Course: {course_name} - Instructors"]
                for instructor in instructors:
                    name = instructor.get("name", "")
                    designation = instructor.get("designation", "")
                    experience = instructor.get("experience", "")
                    instructor_lines.append(f"{name} - {designation}, {experience}")
                
                instructor_text = "\n".join(instructor_lines)
                for chunk_text in s.split_text(instructor_text):
                    all_chunks.append({
                        "text": chunk_text,
                        "metadata": {"source": course_url, "course": course_name, "type": "instructors"}
                    })
            
            # 7. Mentors (Grouped)
            mentors = details.get("mentors", [])
            if mentors:
                mentor_lines = [f"Course: {course_name} - Mentors"]
                for mentor in mentors:
                    name = mentor.get("name", "")
                    expertise = mentor.get("expertise", "")
                    experience = mentor.get("experience", "")
                    mentor_lines.append(f"{name} - {expertise}, {experience}")
                
                mentor_text = "\n".join(mentor_lines)
                for chunk_text in s.split_text(mentor_text):
                    all_chunks.append({
                        "text": chunk_text,
                        "metadata": {"source": course_url, "course": course_name, "type": "mentors"}
                    })
            
            # 8. Tools (Grouped)
            tools = details.get("tools_you_learn", [])
            if tools:
                tools_text = f"Course: {course_name} - Tools You Learn\n" + ", ".join(tools)
                for chunk_text in s.split_text(tools_text):
                    all_chunks.append({
                        "text": chunk_text,
                        "metadata": {"source": course_url, "course": course_name, "type": "tools"}
                    })

    return all_chunks

def main():
    print("Loading data...")
    data = load_data()
    if not data:
        return

    print("Creating text chunks...")
    chunks = create_chunks(data)
    print(f"Created {len(chunks)} chunks.")
    if len(chunks) == 0:
        print("Warning: No chunks created. Check data file content.")
        return

    print(f"Loading embedding model: {MODEL_NAME}...")
    try:
        model = SentenceTransformer(MODEL_NAME)
    except Exception as e:
        print(f"Error loading model: {e}")
        return

    print("Generating embeddings...")
    texts = [chunk["text"] for chunk in chunks]
    try:
        embeddings = model.encode(texts, show_progress_bar=True)
    except Exception as e:
        print(f"Error during encoding: {e}")
        return
    
    print(f"Embeddings shape: {embeddings.shape}")

    print(f"Saving to {CHUNKS_FILE} and {EMBEDDINGS_FILE}...")
    try:
        with open(CHUNKS_FILE, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, indent=2)
        np.save(EMBEDDINGS_FILE, embeddings)
    except Exception as e:
        print(f"Error saving files: {e}")
        return
    
    # Simple verification query (simulated)
    print("Verifying with a test query (Cosine Similarity)...")
    query = "What is the duration of the PM Fellowship?"
    query_embedding = model.encode([query])
    
    # Cosine Similarity: (A . B) / (||A|| * ||B||)
    # Normalize vectors
    norm_embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
    norm_query = query_embedding / np.linalg.norm(query_embedding, axis=1, keepdims=True)
    
    similarities = np.dot(norm_embeddings, norm_query.T).flatten()
    best_idx = np.argmax(similarities)
    best_score = similarities[best_idx]
    
    print(f"Top result (Score: {best_score:.4f}):")
    print(chunks[best_idx]["text"][:200] + "...")

    # Export to SQL
    print("Exporting embeddings to SQL file...")
    sql_file_path = os.path.join(EMBEDDING_DIR, "embeddings.sql")
    export_to_sql(chunks, embeddings, sql_file_path)

    print("Done.")

def export_to_sql(chunks, embeddings, output_file):
    table_name = "course_embeddings"
    create_table_stmt = f"""
CREATE TABLE IF NOT EXISTS {table_name} (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT,
    metadata JSON,
    embedding_vector JSON -- Stored as JSON array
);
"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("-- Auto-generated SQL dump for NextLeap Course Embeddings\n")
        f.write(create_table_stmt + "\n")
        f.write("BEGIN TRANSACTION;\n")
        
        for i, chunk in enumerate(chunks):
            content = chunk["text"].replace("'", "''") # Basic SQL escaping for single quotes
            metadata = json.dumps(chunk["metadata"]).replace("'", "''")
            vector = json.dumps(embeddings[i].tolist())
            
            insert_stmt = f"INSERT INTO {table_name} (content, metadata, embedding_vector) VALUES ('{content}', '{metadata}', '{vector}');\n"
            f.write(insert_stmt)
            
        f.write("COMMIT;\n")
    
    print(f"SQL file created at: {output_file}")

if __name__ == "__main__":
    main()
