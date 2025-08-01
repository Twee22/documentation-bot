#!/usr/bin/env python3
"""
Test script to verify the documentation bot core functionality.
This script tests the basic functionality without making actual API calls.
"""

import os
import tempfile
import shutil
from pathlib import Path

from documentation_bot import RepositoryAnalyzer, DocumentationBot


def test_repository_analysis():
    """Test repository analysis functionality."""
    print("Testing repository analysis...")
    
    # Create a temporary repository
    temp_dir = tempfile.mkdtemp()
    repo_path = Path(temp_dir) / "test_repo"
    repo_path.mkdir()
    
    # Create various files
    (repo_path / "app.py").write_text("from flask import Flask")
    (repo_path / "requirements.txt").write_text("flask==2.3.0\nrequests==2.28.0")
    (repo_path / "config.json").write_text('{"debug": true}')
    (repo_path / "README.md").write_text("# Test Project")
    
    try:
        # Test repository analysis
        analyzer = RepositoryAnalyzer(repo_path)
        analysis = analyzer.analyze()
        
        # Verify analysis results
        assert analysis['project_type'] == 'Python', f"Expected Python, got {analysis['project_type']}"
        assert 'Python' in analysis['languages'], "Python should be detected"
        assert '.py' in analysis['file_types'], ".py should be detected"
        assert 'app.py' in analysis['main_files'], "app.py should be detected as main file"
        assert 'requirements.txt' in analysis['config_files'], "requirements.txt should be detected as config file"
        assert 'flask==2.3.0' in analysis['dependencies'], "Dependencies should be extracted"
        
        print("✅ Repository analysis test passed!")
        
    except Exception as e:
        print(f"❌ Repository analysis test failed: {e}")
        raise
    finally:
        # Cleanup
        shutil.rmtree(temp_dir)


def test_documentation_bot_initialization():
    """Test DocumentationBot initialization."""
    print("Testing DocumentationBot initialization...")
    
    # Create a temporary repository
    temp_dir = tempfile.mkdtemp()
    repo_path = Path(temp_dir) / "test_repo"
    repo_path.mkdir()
    
    try:
        # Test DocumentationBot initialization
        bot = DocumentationBot(
            repo_path=str(repo_path),
            detail_level="high",
            max_llm_calls=15
        )
        
        # Verify initialization
        assert bot.repo_path == repo_path, "Repository path should match"
        assert bot.detail_level == "high", "Detail level should match"
        assert bot.max_llm_calls == 15, "Max LLM calls should match"
        
        print("✅ DocumentationBot initialization test passed!")
        
    except Exception as e:
        print(f"❌ DocumentationBot initialization test failed: {e}")
        raise
    finally:
        # Cleanup
        shutil.rmtree(temp_dir)


def test_error_handling():
    """Test error handling for invalid inputs."""
    print("Testing error handling...")
    
    # Create a temporary repository
    temp_dir = tempfile.mkdtemp()
    repo_path = Path(temp_dir) / "test_repo"
    repo_path.mkdir()
    
    try:
        # Test invalid repository path
        try:
            DocumentationBot(
                repo_path="/nonexistent/path",
                detail_level="medium",
                max_llm_calls=5
            )
            assert False, "Should have raised ValueError for invalid repo path"
        except ValueError as e:
            assert "does not exist" in str(e), "Error should mention path does not exist"
        
        # Test invalid detail level
        try:
            DocumentationBot(
                repo_path=str(repo_path),
                detail_level="invalid",
                max_llm_calls=5
            )
            assert False, "Should have raised ValueError for invalid detail level"
        except ValueError as e:
            assert "Detail level must be" in str(e), "Error should mention detail level"
        
        # Test invalid max_llm_calls
        try:
            DocumentationBot(
                repo_path=str(repo_path),
                detail_level="medium",
                max_llm_calls=-1
            )
            assert False, "Should have raised ValueError for invalid max_llm_calls"
        except ValueError as e:
            assert "Max LLM calls must be positive" in str(e), "Error should mention max_llm_calls"
        
        print("✅ Error handling test passed!")
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        raise
    finally:
        # Cleanup
        shutil.rmtree(temp_dir)


def test_file_filtering():
    """Test that binary and large files are properly filtered."""
    print("Testing file filtering...")
    
    # Create a temporary repository
    temp_dir = tempfile.mkdtemp()
    repo_path = Path(temp_dir) / "test_repo"
    repo_path.mkdir()
    
    try:
        # Create a binary file with null bytes
        (repo_path / "binary.jpg").write_bytes(b'\xff\xd8\xff\xe0\x00\x00\x00\x00')
        
        # Create a large file (over 1MB)
        large_content = "x" * (1024 * 1024 + 100)
        (repo_path / "large_file.txt").write_text(large_content)
        
        # Create a normal text file
        (repo_path / "normal.py").write_text("print('hello')")
        
        # Test repository analysis
        analyzer = RepositoryAnalyzer(repo_path)
        analysis = analyzer.analyze()
        
        # Verify that binary and large files are filtered out
        assert 'normal.py' in analysis['structure'], "Normal file should be included"
        assert 'binary.jpg' not in analysis['structure'], "Binary file should be filtered out"
        assert 'large_file.txt' not in analysis['structure'], "Large file should be filtered out"
        
        print("✅ File filtering test passed!")
        
    except Exception as e:
        print(f"❌ File filtering test failed: {e}")
        raise
    finally:
        # Cleanup
        shutil.rmtree(temp_dir)


def main():
    """Run all tests."""
    print("🧪 Running Documentation Bot Core Tests\n")
    
    try:
        test_repository_analysis()
        test_documentation_bot_initialization()
        test_error_handling()
        test_file_filtering()
        
        print("\n🎉 All tests passed! The documentation bot core functionality is working correctly.")
        print("\nTo use the documentation bot with real API calls:")
        print("1. Install OpenAI: pip install openai")
        print("2. Set your OpenAI API key: export OPENAI_API_KEY='your-key-here'")
        print("3. Run: python documentation_bot.py --repo-path /path/to/repo")
        
    except Exception as e:
        print(f"\n❌ Tests failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main()) 