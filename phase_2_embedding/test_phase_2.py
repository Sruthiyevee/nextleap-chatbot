
import unittest
import os
import json
import numpy as np
import sys

# Add parent directory to path to allow importing modules if needed
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class TestPhase2Embeddings(unittest.TestCase):
    def setUp(self):
        self.embeddings_dir = os.path.dirname(os.path.abspath(__file__))
        self.chunks_file = os.path.join(self.embeddings_dir, "chunks.json")
        self.embeddings_npy = os.path.join(self.embeddings_dir, "embeddings.npy")
        self.embeddings_sql = os.path.join(self.embeddings_dir, "embeddings.sql")

    def test_artifacts_exist(self):
        """Verify that all expected output files exist."""
        self.assertTrue(os.path.exists(self.chunks_file), "chunks.json not found")
        self.assertTrue(os.path.exists(self.embeddings_npy), "embeddings.npy not found")
        self.assertTrue(os.path.exists(self.embeddings_sql), "embeddings.sql not found")

    def test_chunks_integrity(self):
        """Verify the content of chunks.json."""
        with open(self.chunks_file, 'r', encoding='utf-8') as f:
            chunks = json.load(f)
        
        self.assertIsInstance(chunks, list, "Chunks should be a list")
        self.assertTrue(len(chunks) > 0, "Chunks list should not be empty")
        
        first_chunk = chunks[0]
        self.assertIn("text", first_chunk, "Chunk missing 'text' field")
        self.assertIn("metadata", first_chunk, "Chunk missing 'metadata' field")
        
        # Verify metadata structure
        metadata = first_chunk["metadata"]
        self.assertIn("course", metadata, "Metadata missing 'course'")
        self.assertIn("type", metadata, "Metadata missing 'type'")

    def test_embeddings_shape(self):
        """Verify embeddings.npy matches chunks count and embedding dimension."""
        with open(self.chunks_file, 'r', encoding='utf-8') as f:
            chunks = json.load(f)
            
        embeddings = np.load(self.embeddings_npy)
        
        self.assertEqual(len(chunks), embeddings.shape[0], 
                         f"Number of chunks ({len(chunks)}) does not match embeddings shape ({embeddings.shape[0]})")
        
        # sentence-transformers/all-MiniLM-L6-v2 outputs 384 dimensions
        self.assertEqual(embeddings.shape[1], 384, 
                         f"Embedding dimension should be 384, got {embeddings.shape[1]}")

    def test_sql_file_content(self):
        """Basic check if SQL file is not empty."""
        file_size = os.path.getsize(self.embeddings_sql)
        self.assertTrue(file_size > 0, "embeddings.sql is empty")
        
        with open(self.embeddings_sql, 'r', encoding='utf-8') as f:
            header = f.readline()
            self.assertIn("-- Auto-generated SQL dump", header, "SQL file header mismatch")

    def test_create_embeddings_import(self):
        """Verify create_embeddings.py is importable (syntax check)."""
        try:
            import create_embeddings
        except ImportError:
            self.fail("Could not import create_embeddings.py")
        except Exception as e:
            self.fail(f"Importing create_embeddings.py raised exception: {e}")

if __name__ == '__main__':
    unittest.main()
