#!/usr/bin/env python3
"""
Demo script for the Documentation Bot system.
This script demonstrates how to use the documentation bot to analyze a repository.
"""

import tempfile
import shutil
from pathlib import Path
from documentation_bot import RepositoryAnalyzer, DocumentationBot


def create_sample_repository():
    """Create a sample repository for demonstration purposes."""
    temp_dir = tempfile.mkdtemp()
    repo_path = Path(temp_dir) / "sample_repo"
    repo_path.mkdir()
    
    # Create a sample Python Flask application
    (repo_path / "app.py").write_text("""
from flask import Flask, jsonify, request
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the API!"})

@app.route('/api/users', methods=['GET'])
def get_users():
    return jsonify({"users": ["Alice", "Bob", "Charlie"]})

@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()
    return jsonify({"message": f"Created user: {data.get('name')}"})

if __name__ == '__main__':
    app.run(debug=True)
""")
    
    (repo_path / "requirements.txt").write_text("""
flask==2.3.0
flask-cors==4.0.0
python-dotenv==1.0.0
""")
    
    (repo_path / "config.py").write_text("""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
""")
    
    (repo_path / "models.py").write_text("""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    
    def __repr__(self):
        return f'<User {self.username}>'
""")
    
    (repo_path / "README.md").write_text("# Sample Flask API\n\nThis is a sample Flask API application.")
    
    return repo_path


def demo_repository_analysis():
    """Demonstrate repository analysis functionality."""
    print("=== Documentation Bot Demo ===\n")
    
    # Create a sample repository
    print("1. Creating sample repository...")
    repo_path = create_sample_repository()
    print(f"   Sample repository created at: {repo_path}\n")
    
    # Analyze the repository
    print("2. Analyzing repository...")
    analyzer = RepositoryAnalyzer(repo_path)
    analysis = analyzer.analyze()
    
    print("   Analysis Results:")
    print(f"   - Project Type: {analysis['project_type']}")
    print(f"   - Languages: {', '.join(analysis['languages'])}")
    print(f"   - File Types: {', '.join(analysis['file_types'])}")
    print(f"   - Main Files: {', '.join(analysis['main_files'])}")
    print(f"   - Config Files: {', '.join(analysis['config_files'])}")
    print(f"   - Dependencies: {', '.join(analysis['dependencies'])}")
    print(f"   - Total Files: {len(analysis['structure'])}")
    print()
    
    # Show file structure
    print("   File Structure:")
    for file_path in analysis['structure']:
        print(f"   - {file_path}")
    print()
    
    # Demonstrate DocumentationBot initialization
    print("3. Initializing DocumentationBot...")
    try:
        bot = DocumentationBot(
            repo_path=str(repo_path),
            detail_level="medium",
            max_llm_calls=10
        )
        print("   DocumentationBot initialized successfully!")
        print(f"   - Repository Path: {bot.repo_path}")
        print(f"   - Detail Level: {bot.detail_level}")
        print(f"   - Max LLM Calls: {bot.max_llm_calls}")
        print()
        
        print("4. Note: Documentation generation requires OpenAI API key")
        print("   To generate actual documentation, you would need to:")
        print("   - Set OPENAI_API_KEY environment variable")
        print("   - Install OpenAI library: pip install openai")
        print("   - Call bot.generate_documentation()")
        print()
        
    except ImportError as e:
        print(f"   Warning: {e}")
        print("   This is expected when OpenAI is not installed.")
        print()
    
    # Cleanup
    print("5. Cleaning up...")
    shutil.rmtree(repo_path.parent)
    print("   Demo completed!")
    
    return analysis


def demo_command_line_usage():
    """Demonstrate command line usage."""
    print("=== Command Line Usage Demo ===\n")
    
    print("To use the documentation bot from command line:")
    print()
    print("1. Basic usage:")
    print("   python documentation_bot.py --repo-path /path/to/your/repository")
    print()
    print("2. With custom settings:")
    print("   python documentation_bot.py \\")
    print("     --repo-path /path/to/your/repository \\")
    print("     --detail-level high \\")
    print("     --max-llm-calls 30")
    print()
    print("3. Available options:")
    print("   --repo-path: Path to repository (required)")
    print("   --detail-level: low, medium, or high (default: medium)")
    print("   --max-llm-calls: Maximum API calls (default: 20)")
    print()
    print("4. Example with sample repository:")
    print("   python documentation_bot.py --repo-path ./sample_repo --detail-level medium")
    print()


if __name__ == "__main__":
    # Run the demo
    analysis = demo_repository_analysis()
    
    print("\n" + "="*50 + "\n")
    
    # Show command line usage
    demo_command_line_usage()
    
    print("\n" + "="*50)
    print("Demo completed successfully!")
    print("The Documentation Bot is ready to use!") 