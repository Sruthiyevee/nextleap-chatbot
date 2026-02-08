
import sqlite3
import os
import sys

# Configuration
# Path to the SQL file generated in Phase 2
SQL_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "phase_2_embedding", "embeddings.sql"))
# Path to the new SQLite database
DB_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "knowledge_base.db"))

def init_db():
    print(f"Checking for SQL dump at: {SQL_FILE}")
    if not os.path.exists(SQL_FILE):
        print("Error: embeddings.sql file not found. Please complete Phase 2 first.")
        sys.exit(1)

    print(f"Initializing database at: {DB_FILE}")
    
    # Remove existing DB if it exists to ensure clean state
    if os.path.exists(DB_FILE):
        print("Removing existing database...")
        os.remove(DB_FILE)

    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        print("Reading SQL dump...")
        with open(SQL_FILE, 'r', encoding='utf-8') as f:
            sql_script = f.read()
            
        print("Executing SQL script...")
        cursor.executescript(sql_script)
        
        conn.commit()
        
        # Verify
        cursor.execute("SELECT Count(*) FROM course_embeddings")
        count = cursor.fetchone()[0]
        print(f"Success! Database initialized with {count} records.")
        
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    init_db()
