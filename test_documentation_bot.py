import unittest
import tempfile
import os
import shutil
from unittest.mock import patch, MagicMock
from pathlib import Path

# Import the main classes we'll create
from documentation_bot import DocumentationBot, RepositoryAnalyzer, DocumentationGenerator


class TestDocumentationBot(unittest.TestCase):
    """Test cases for the main DocumentationBot class."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.repo_path = Path(self.temp_dir) / "test_repo"
        self.repo_path.mkdir()
        
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_initialization_with_valid_repo_path(self):
        """Test that DocumentationBot initializes correctly with valid repo path."""
        bot = DocumentationBot(
            repo_path=str(self.repo_path),
            detail_level="medium",
            max_llm_calls=10
        )
        self.assertEqual(bot.repo_path, self.repo_path)
        self.assertEqual(bot.detail_level, "medium")
        self.assertEqual(bot.max_llm_calls, 10)
    
    def test_initialization_with_invalid_repo_path(self):
        """Test that DocumentationBot raises error with invalid repo path."""
        with self.assertRaises(ValueError):
            DocumentationBot(
                repo_path="/nonexistent/path",
                detail_level="medium",
                max_llm_calls=10
            )
    
    def test_invalid_detail_level(self):
        """Test that DocumentationBot raises error with invalid detail level."""
        with self.assertRaises(ValueError):
            DocumentationBot(
                repo_path=str(self.repo_path),
                detail_level="invalid",
                max_llm_calls=10
            )
    
    def test_invalid_max_llm_calls(self):
        """Test that DocumentationBot raises error with invalid max_llm_calls."""
        with self.assertRaises(ValueError):
            DocumentationBot(
                repo_path=str(self.repo_path),
                detail_level="medium",
                max_llm_calls=-1
            )


class TestRepositoryAnalyzer(unittest.TestCase):
    """Test cases for the RepositoryAnalyzer class."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.repo_path = Path(self.temp_dir) / "test_repo"
        self.repo_path.mkdir()
        self.analyzer = RepositoryAnalyzer(self.repo_path)
        
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_analyze_empty_repository(self):
        """Test analyzing an empty repository."""
        result = self.analyzer.analyze()
        self.assertIsInstance(result, dict)
        self.assertIn('file_types', result)
        self.assertIn('languages', result)
        self.assertIn('structure', result)
        self.assertEqual(len(result['file_types']), 0)
    
    def test_analyze_python_repository(self):
        """Test analyzing a Python repository."""
        # Create some Python files
        (self.repo_path / "main.py").write_text("print('Hello, World!')")
        (self.repo_path / "utils.py").write_text("def helper(): pass")
        (self.repo_path / "requirements.txt").write_text("requests==2.28.0")
        
        result = self.analyzer.analyze()
        self.assertIn('.py', result['file_types'])
        self.assertIn('Python', result['languages'])
        self.assertIn('main.py', result['structure'])
    
    def test_analyze_mixed_repository(self):
        """Test analyzing a repository with multiple file types."""
        # Create various file types
        (self.repo_path / "app.py").write_text("from flask import Flask")
        (self.repo_path / "index.html").write_text("<html></html>")
        (self.repo_path / "style.css").write_text("body { margin: 0; }")
        (self.repo_path / "config.json").write_text('{"debug": true}')
        
        result = self.analyzer.analyze()
        self.assertIn('.py', result['file_types'])
        self.assertIn('.html', result['file_types'])
        self.assertIn('.css', result['file_types'])
        self.assertIn('.json', result['file_types'])
    
    def test_ignore_binary_files(self):
        """Test that binary files are ignored."""
        # Create a binary-like file
        (self.repo_path / "image.jpg").write_bytes(b'\xff\xd8\xff\xe0')
        (self.repo_path / "data.py").write_text("import os")
        
        result = self.analyzer.analyze()
        self.assertIn('.py', result['file_types'])
        self.assertNotIn('.jpg', result['file_types'])


class TestDocumentationGenerator(unittest.TestCase):
    """Test cases for the DocumentationGenerator class."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.repo_path = Path(self.temp_dir) / "test_repo"
        self.repo_path.mkdir()
        self.generator = DocumentationGenerator(
            repo_path=self.repo_path,
            detail_level="medium",
            max_llm_calls=10
        )
        
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    @patch('documentation_bot.openai.ChatCompletion.create')
    def test_generate_readme(self, mock_openai):
        """Test generating a README.md file."""
        mock_openai.return_value.choices[0].message.content = "# Test README\n\nThis is a test."
        
        # Create some files to analyze
        (self.repo_path / "main.py").write_text("print('Hello')")
        
        self.generator.generate_readme()
        
        readme_path = self.repo_path / "README.md"
        self.assertTrue(readme_path.exists())
        self.assertIn("Test README", readme_path.read_text())
    
    @patch('documentation_bot.openai.ChatCompletion.create')
    def test_generate_documentation_files(self, mock_openai):
        """Test generating documentation files in /docs directory."""
        mock_openai.return_value.choices[0].message.content = "# API Documentation\n\nTest content."
        
        # Create some files to analyze
        (self.repo_path / "app.py").write_text("from flask import Flask")
        (self.repo_path / "models.py").write_text("class User: pass")
        
        self.generator.generate_documentation_files()
        
        docs_path = self.repo_path / "docs"
        self.assertTrue(docs_path.exists())
        self.assertTrue(docs_path.is_dir())
    
    def test_different_detail_levels(self):
        """Test that different detail levels affect documentation generation."""
        # Test high detail level
        high_generator = DocumentationGenerator(
            repo_path=self.repo_path,
            detail_level="high",
            max_llm_calls=10
        )
        self.assertEqual(high_generator.detail_level, "high")
        
        # Test low detail level
        low_generator = DocumentationGenerator(
            repo_path=self.repo_path,
            detail_level="low",
            max_llm_calls=10
        )
        self.assertEqual(low_generator.detail_level, "low")
    
    def test_llm_call_counting(self):
        """Test that LLM calls are properly counted and limited."""
        generator = DocumentationGenerator(
            repo_path=self.repo_path,
            detail_level="medium",
            max_llm_calls=2
        )
        
        self.assertEqual(generator.llm_calls_made, 0)
        self.assertEqual(generator.max_llm_calls, 2)


class TestMainCLI(unittest.TestCase):
    """Test cases for the command-line interface."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.repo_path = Path(self.temp_dir) / "test_repo"
        self.repo_path.mkdir()
        
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    @patch('documentation_bot.DocumentationBot')
    def test_main_with_valid_arguments(self, mock_bot):
        """Test main function with valid command line arguments."""
        from documentation_bot import main
        
        with patch('sys.argv', [
            'documentation_bot.py',
            '--repo-path', str(self.repo_path),
            '--detail-level', 'medium',
            '--max-llm-calls', '10'
        ]):
            main()
            mock_bot.assert_called_once()
    
    @patch('documentation_bot.DocumentationBot')
    def test_main_with_defaults(self, mock_bot):
        """Test main function with default arguments."""
        from documentation_bot import main
        
        with patch('sys.argv', [
            'documentation_bot.py',
            '--repo-path', str(self.repo_path)
        ]):
            main()
            mock_bot.assert_called_once()


if __name__ == '__main__':
    unittest.main() 