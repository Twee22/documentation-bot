#!/usr/bin/env python3
"""
Basic tests for the documentation bot that don't require external dependencies.
"""

import unittest
import tempfile
import os
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import the classes we'll test
from documentation_bot import RepositoryAnalyzer, DocumentationBot


class TestRepositoryAnalyzerBasic(unittest.TestCase):
    """Basic test cases for RepositoryAnalyzer that don't require OpenAI."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.repo_path = Path(self.temp_dir) / "test_repo"
        self.repo_path.mkdir()
        
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_initialization_with_valid_repo_path(self):
        """Test that RepositoryAnalyzer initializes correctly with valid repo path."""
        analyzer = RepositoryAnalyzer(self.repo_path)
        self.assertEqual(analyzer.repo_path, self.repo_path)
    
    def test_initialization_with_invalid_repo_path(self):
        """Test that RepositoryAnalyzer raises error with invalid repo path."""
        with self.assertRaises(ValueError):
            RepositoryAnalyzer("/nonexistent/path")
    
    def test_analyze_empty_repository(self):
        """Test analyzing an empty repository."""
        analyzer = RepositoryAnalyzer(self.repo_path)
        result = analyzer.analyze()
        
        self.assertIsInstance(result, dict)
        self.assertIn('file_types', result)
        self.assertIn('languages', result)
        self.assertIn('structure', result)
        self.assertIn('main_files', result)
        self.assertIn('config_files', result)
        self.assertIn('dependencies', result)
        self.assertIn('project_type', result)
        
        self.assertEqual(len(result['file_types']), 0)
        self.assertEqual(len(result['languages']), 0)
        self.assertEqual(len(result['structure']), 0)
        self.assertEqual(result['project_type'], 'unknown')
    
    def test_analyze_python_repository(self):
        """Test analyzing a Python repository."""
        # Create some Python files
        (self.repo_path / "main.py").write_text("print('Hello, World!')")
        (self.repo_path / "utils.py").write_text("def helper(): pass")
        (self.repo_path / "requirements.txt").write_text("requests==2.28.0\nflask==2.3.0")
        
        analyzer = RepositoryAnalyzer(self.repo_path)
        result = analyzer.analyze()
        
        self.assertIn('.py', result['file_types'])
        self.assertIn('.txt', result['file_types'])
        self.assertIn('Python', result['languages'])
        self.assertIn('main.py', result['structure'])
        self.assertIn('utils.py', result['structure'])
        self.assertIn('requirements.txt', result['structure'])
        self.assertIn('main.py', result['main_files'])
        self.assertIn('requirements.txt', result['config_files'])
        self.assertIn('requests==2.28.0', result['dependencies'])
        self.assertIn('flask==2.3.0', result['dependencies'])
        self.assertEqual(result['project_type'], 'Python')
    
    def test_analyze_mixed_repository(self):
        """Test analyzing a repository with multiple file types."""
        # Create various file types
        (self.repo_path / "app.py").write_text("from flask import Flask")
        (self.repo_path / "index.html").write_text("<html></html>")
        (self.repo_path / "style.css").write_text("body { margin: 0; }")
        (self.repo_path / "config.json").write_text('{"debug": true}')
        (self.repo_path / "package.json").write_text('{"name": "test-app"}')
        
        analyzer = RepositoryAnalyzer(self.repo_path)
        result = analyzer.analyze()
        
        self.assertIn('.py', result['file_types'])
        self.assertIn('.html', result['file_types'])
        self.assertIn('.css', result['file_types'])
        self.assertIn('.json', result['file_types'])
        
        self.assertIn('Python', result['languages'])
        self.assertIn('HTML', result['languages'])
        self.assertIn('CSS', result['languages'])
        self.assertIn('JSON', result['languages'])
        
        self.assertIn('app.py', result['main_files'])
        self.assertIn('config.json', result['config_files'])
        self.assertIn('package.json', result['config_files'])
    
    def test_ignore_binary_files(self):
        """Test that binary files are ignored."""
        # Create a binary-like file with null bytes
        (self.repo_path / "image.jpg").write_bytes(b'\xff\xd8\xff\xe0\x00\x00\x00\x00')
        (self.repo_path / "data.py").write_text("import os")
        
        analyzer = RepositoryAnalyzer(self.repo_path)
        result = analyzer.analyze()
        
        self.assertIn('.py', result['file_types'])
        self.assertNotIn('.jpg', result['file_types'])
        self.assertIn('data.py', result['structure'])
        self.assertNotIn('image.jpg', result['structure'])
    
    def test_ignore_large_files(self):
        """Test that large files are ignored."""
        # Create a large file (over 1MB)
        large_file = self.repo_path / "large_file.txt"
        large_content = "x" * (1024 * 1024 + 100)  # Just over 1MB
        large_file.write_text(large_content)
        
        (self.repo_path / "small_file.py").write_text("print('hello')")
        
        analyzer = RepositoryAnalyzer(self.repo_path)
        result = analyzer.analyze()
        
        self.assertIn('.py', result['file_types'])
        self.assertNotIn('.txt', result['file_types'])
        self.assertIn('small_file.py', result['structure'])
        self.assertNotIn('large_file.txt', result['structure'])
    
    def test_ignore_common_directories(self):
        """Test that common directories are ignored."""
        # Create ignored directories
        (self.repo_path / ".git").mkdir()
        (self.repo_path / ".git" / "config").write_text("git config")
        
        (self.repo_path / "__pycache__").mkdir()
        (self.repo_path / "__pycache__" / "test.pyc").write_bytes(b'\x00\x00\x00\x00')
        
        (self.repo_path / "node_modules").mkdir()
        (self.repo_path / "node_modules" / "package.json").write_text('{"name": "test"}')
        
        # Create regular files
        (self.repo_path / "main.py").write_text("print('hello')")
        (self.repo_path / "README.md").write_text("# Test")
        
        analyzer = RepositoryAnalyzer(self.repo_path)
        result = analyzer.analyze()
        
        self.assertIn('.py', result['file_types'])
        self.assertIn('.md', result['file_types'])
        self.assertIn('main.py', result['structure'])
        self.assertIn('README.md', result['structure'])
        
        # Should not include files from ignored directories
        self.assertNotIn('.git/config', result['structure'])
        self.assertNotIn('__pycache__/test.pyc', result['structure'])
        self.assertNotIn('node_modules/package.json', result['structure'])


class TestDocumentationBotBasic(unittest.TestCase):
    """Basic test cases for DocumentationBot that don't require OpenAI."""
    
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
    
    def test_valid_detail_levels(self):
        """Test that all valid detail levels work."""
        for level in ["low", "medium", "high"]:
            bot = DocumentationBot(
                repo_path=str(self.repo_path),
                detail_level=level,
                max_llm_calls=10
            )
            self.assertEqual(bot.detail_level, level)


if __name__ == '__main__':
    unittest.main() 