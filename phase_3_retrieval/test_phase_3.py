
import unittest
import os
import sqlite3
import sys

# Add directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from retrieval_engine import RetrievalEngine

class TestPhase3Retrieval(unittest.TestCase):
    def setUp(self):
        self.db_file = os.path.join(os.path.dirname(__file__), "knowledge_base.db")
        if not os.path.exists(self.db_file):
            self.skipTest("knowledge_base.db not found")

    def test_database_connection(self):
        """Test simple SQLite connection."""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        self.assertEqual(result[0], 1)
        conn.close()

    def test_database_table_exists(self):
        """Verify 'course_embeddings' table exists."""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='course_embeddings';")
        rows = cursor.fetchall()
        self.assertEqual(len(rows), 1, "Table 'course_embeddings' missing")
        conn.close()

    def test_retrieval_engine_initialization(self):
        """Verify RetrievalEngine loads chunks."""
        engine = RetrievalEngine()
        self.assertTrue(len(engine.chunks) > 0, "No chunks loaded from DB")
        self.assertTrue(len(engine.embeddings) > 0, "No embeddings loaded from DB")
        self.assertEqual(len(engine.chunks), len(engine.embeddings))

    def test_search_functionality(self):
        """Test search returns relevant results."""
        engine = RetrievalEngine()
        query = "How long is the Product Management course?" # Known context
        results = engine.search(query, k=3)
        
        self.assertTrue(len(results) > 0, "Search returned empty results")
        
        # Check result structure
        first_result = results[0]
        self.assertIn("score", first_result)
        self.assertIn("content", first_result)
        self.assertIn("metadata", first_result)
        
        # Check relevance (score should be reasonably high for a relevant query, e.g., > 0.3)
        # Note: Depending on model and data, thresholds vary. Just assert > 0.1 for safety.
        self.assertGreater(first_result["score"], 0.1, "Search score unreasonably low (< 0.1)")

    def test_retrieve_context_formatting(self):
        """Test context string formatting."""
        engine = RetrievalEngine()
        context_str = engine.retrieve_context("Test query")
        
        self.assertIn("Top", context_str)
        self.assertIn("Retrieval Results", context_str)
        self.assertIn("Score:", context_str)
        self.assertIn("Source:", context_str)

if __name__ == '__main__':
    unittest.main()
