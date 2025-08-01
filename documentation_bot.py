#!/usr/bin/env python3
"""
Documentation Bot - An agentic system for generating comprehensive documentation
for code repositories using OpenAI's language models.
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

# Try to import optional dependencies
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    def load_dotenv():
        pass

try:
    import openai
except ImportError:
    openai = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RepositoryAnalyzer:
    """Analyzes a code repository to understand its structure and content."""
    
    def __init__(self, repo_path: Path):
        """Initialize the analyzer with the repository path."""
        self.repo_path = Path(repo_path)
        if not self.repo_path.exists():
            raise ValueError(f"Repository path does not exist: {repo_path}")
    
    def analyze(self) -> Dict[str, Any]:
        """Analyze the repository and return structured information."""
        logger.info(f"Analyzing repository: {self.repo_path}")
        
        result = {
            'file_types': set(),
            'languages': set(),
            'structure': [],
            'main_files': [],
            'config_files': [],
            'dependencies': [],
            'project_type': 'unknown'
        }
        
        # Walk through all files in the repository
        for file_path in self.repo_path.rglob('*'):
            if file_path.is_file() and not self._should_ignore_file(file_path):
                relative_path = file_path.relative_to(self.repo_path)
                result['structure'].append(str(relative_path))
                
                # Analyze file extension
                suffix = file_path.suffix.lower()
                if suffix:
                    result['file_types'].add(suffix)
                
                # Determine language and project type
                self._analyze_file(file_path, result)
        
        # Convert sets to lists for JSON serialization
        result['file_types'] = list(result['file_types'])
        result['languages'] = list(result['languages'])
        
        logger.info(f"Analysis complete. Found {len(result['structure'])} files.")
        return result
    
    def _should_ignore_file(self, file_path: Path) -> bool:
        """Determine if a file should be ignored during analysis."""
        # Ignore common directories
        ignore_dirs = {'.git', '__pycache__', '.pytest_cache', 'node_modules', '.venv', 'venv'}
        if any(part in ignore_dirs for part in file_path.parts):
            return True
        
        # Ignore binary files and large files
        if file_path.stat().st_size > 1024 * 1024:  # 1MB limit
            return True
        
        # Check if file is binary by looking for null bytes
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                if b'\x00' in chunk:
                    return True
        except:
            return True
        
        return False
    
    def _analyze_file(self, file_path: Path, result: Dict[str, Any]):
        """Analyze a specific file and update the result dictionary."""
        filename = file_path.name.lower()
        suffix = file_path.suffix.lower()
        
        # Detect main files
        if filename in {'main.py', 'app.py', 'index.py', 'run.py'}:
            result['main_files'].append(str(file_path.relative_to(self.repo_path)))
        
        # Detect config files
        if filename in {'requirements.txt', 'package.json', 'setup.py', 'pyproject.toml', 
                       'dockerfile', 'docker-compose.yml', '.env.example', 'config.json'}:
            result['config_files'].append(str(file_path.relative_to(self.repo_path)))
        
        # Detect languages and project types
        if suffix == '.py':
            result['languages'].add('Python')
            if not result['project_type'] or result['project_type'] == 'unknown':
                result['project_type'] = 'Python'
        elif suffix in {'.js', '.jsx', '.ts', '.tsx'}:
            result['languages'].add('JavaScript')
            if not result['project_type'] or result['project_type'] == 'unknown':
                result['project_type'] = 'JavaScript'
        elif suffix in {'.html', '.htm'}:
            result['languages'].add('HTML')
        elif suffix == '.css':
            result['languages'].add('CSS')
        elif suffix == '.json':
            result['languages'].add('JSON')
        elif suffix == '.md':
            result['languages'].add('Markdown')
        elif suffix in {'.yml', '.yaml'}:
            result['languages'].add('YAML')
        elif suffix == '.txt':
            result['languages'].add('Text')
        
        # Extract dependencies from requirements.txt
        if filename == 'requirements.txt':
            try:
                content = file_path.read_text()
                for line in content.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('#') and '==' in line:
                        result['dependencies'].append(line)
            except:
                pass


class DocumentationGenerator:
    """Generates documentation using OpenAI's language models."""
    
    def __init__(self, repo_path: Path, detail_level: str, max_llm_calls: int):
        """Initialize the documentation generator."""
        self.repo_path = Path(repo_path)
        self.detail_level = detail_level
        self.max_llm_calls = max_llm_calls
        self.llm_calls_made = 0
        
        # Check if OpenAI is available
        if openai is None:
            raise ImportError("OpenAI library is not installed. Please install it with: pip install openai")
        
        # Validate OpenAI API key
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        openai.api_key = api_key
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4')
    
    def generate_readme(self, analysis: Dict[str, Any]) -> None:
        """Generate a README.md file for the repository."""
        if self.llm_calls_made >= self.max_llm_calls:
            logger.warning("Maximum LLM calls reached. Skipping README generation.")
            return
        
        logger.info("Generating README.md...")
        
        # Prepare context for the LLM
        context = self._prepare_readme_context(analysis)
        
        # Generate README content
        readme_content = self._call_llm(
            system_prompt=self._get_readme_system_prompt(),
            user_prompt=context
        )
        
        # Write README file
        readme_path = self.repo_path / "README.md"
        readme_path.write_text(readme_content)
        logger.info(f"README.md created at {readme_path}")
    
    def generate_documentation_files(self, analysis: Dict[str, Any]) -> None:
        """Generate comprehensive documentation files in the /docs directory."""
        if self.llm_calls_made >= self.max_llm_calls:
            logger.warning("Maximum LLM calls reached. Skipping documentation generation.")
            return
        
        logger.info("Generating documentation files...")
        
        # Create docs directory
        docs_path = self.repo_path / "docs"
        docs_path.mkdir(exist_ok=True)
        
        # Generate different types of documentation based on analysis
        self._generate_architecture_doc(analysis, docs_path)
        self._generate_api_doc(analysis, docs_path)
        self._generate_setup_doc(analysis, docs_path)
        self._generate_usage_doc(analysis, docs_path)
        
        logger.info(f"Documentation files created in {docs_path}")
    
    def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """Make a call to the OpenAI API."""
        if self.llm_calls_made >= self.max_llm_calls:
            raise ValueError("Maximum LLM calls reached")
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=4000
            )
            
            self.llm_calls_made += 1
            logger.info(f"LLM call {self.llm_calls_made}/{self.max_llm_calls} completed")
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            raise
    
    def _prepare_readme_context(self, analysis: Dict[str, Any]) -> str:
        """Prepare context information for README generation."""
        context = f"""
Repository Analysis:
- Project Type: {analysis.get('project_type', 'Unknown')}
- Languages: {', '.join(analysis.get('languages', []))}
- File Types: {', '.join(analysis.get('file_types', []))}
- Main Files: {', '.join(analysis.get('main_files', []))}
- Config Files: {', '.join(analysis.get('config_files', []))}
- Dependencies: {', '.join(analysis.get('dependencies', []))}

Repository Structure:
{chr(10).join(analysis.get('structure', []))}

Detail Level: {self.detail_level}

Please generate a comprehensive README.md file for this repository.
"""
        return context
    
    def _get_readme_system_prompt(self) -> str:
        """Get the system prompt for README generation."""
        detail_instructions = {
            'low': "Provide a basic overview with minimal technical details.",
            'medium': "Include setup instructions, basic usage, and key features.",
            'high': "Include detailed setup instructions, code examples, architecture overview, and comprehensive feature documentation."
        }
        
        return f"""You are an expert technical writer creating README.md files for software projects.

Detail Level: {self.detail_level}
Instructions: {detail_instructions.get(self.detail_level, detail_instructions['medium'])}

Create a well-structured README.md that includes:
1. Project title and description
2. Features and capabilities
3. Installation and setup instructions
4. Usage examples
5. Project structure overview
6. Contributing guidelines (if applicable)
7. License information (if available)

Use proper Markdown formatting and make it professional and informative."""
    
    def _generate_architecture_doc(self, analysis: Dict[str, Any], docs_path: Path) -> None:
        """Generate architecture documentation."""
        if self.llm_calls_made >= self.max_llm_calls:
            return
        
        context = self._prepare_architecture_context(analysis)
        content = self._call_llm(
            system_prompt=self._get_architecture_system_prompt(),
            user_prompt=context
        )
        
        arch_path = docs_path / "architecture.md"
        arch_path.write_text(content)
    
    def _generate_api_doc(self, analysis: Dict[str, Any], docs_path: Path) -> None:
        """Generate API documentation."""
        if self.llm_calls_made >= self.max_llm_calls:
            return
        
        context = self._prepare_api_context(analysis)
        content = self._call_llm(
            system_prompt=self._get_api_system_prompt(),
            user_prompt=context
        )
        
        api_path = docs_path / "api.md"
        api_path.write_text(content)
    
    def _generate_setup_doc(self, analysis: Dict[str, Any], docs_path: Path) -> None:
        """Generate setup documentation."""
        if self.llm_calls_made >= self.max_llm_calls:
            return
        
        context = self._prepare_setup_context(analysis)
        content = self._call_llm(
            system_prompt=self._get_setup_system_prompt(),
            user_prompt=context
        )
        
        setup_path = docs_path / "setup.md"
        setup_path.write_text(content)
    
    def _generate_usage_doc(self, analysis: Dict[str, Any], docs_path: Path) -> None:
        """Generate usage documentation."""
        if self.llm_calls_made >= self.max_llm_calls:
            return
        
        context = self._prepare_usage_context(analysis)
        content = self._call_llm(
            system_prompt=self._get_usage_system_prompt(),
            user_prompt=context
        )
        
        usage_path = docs_path / "usage.md"
        usage_path.write_text(content)
    
    def _prepare_architecture_context(self, analysis: Dict[str, Any]) -> str:
        """Prepare context for architecture documentation."""
        return f"""
Repository Analysis for Architecture Documentation:
- Project Type: {analysis.get('project_type', 'Unknown')}
- Languages: {', '.join(analysis.get('languages', []))}
- Main Files: {', '.join(analysis.get('main_files', []))}
- File Structure: {chr(10).join(analysis.get('structure', []))}

Detail Level: {self.detail_level}

Generate comprehensive architecture documentation including system design, component relationships, and data flow.
"""
    
    def _get_architecture_system_prompt(self) -> str:
        """Get system prompt for architecture documentation."""
        return """You are an expert software architect creating architecture documentation.

Create detailed architecture documentation that includes:
1. System overview and high-level design
2. Component architecture and relationships
3. Data flow and processing
4. Technology stack and dependencies
5. Deployment architecture (if applicable)
6. Security considerations (if applicable)

Use clear diagrams in text format (ASCII art) and provide comprehensive technical details."""
    
    def _prepare_api_context(self, analysis: Dict[str, Any]) -> str:
        """Prepare context for API documentation."""
        return f"""
Repository Analysis for API Documentation:
- Project Type: {analysis.get('project_type', 'Unknown')}
- Languages: {', '.join(analysis.get('languages', []))}
- Main Files: {', '.join(analysis.get('main_files', []))}

Detail Level: {self.detail_level}

Generate comprehensive API documentation including endpoints, parameters, and usage examples.
"""
    
    def _get_api_system_prompt(self) -> str:
        """Get system prompt for API documentation."""
        return """You are an expert API documentation writer.

Create comprehensive API documentation that includes:
1. API overview and purpose
2. Authentication methods (if applicable)
3. Endpoint documentation with parameters
4. Request/response examples
5. Error handling
6. Rate limiting (if applicable)
7. SDK examples (if applicable)

Use clear examples and provide practical usage scenarios."""
    
    def _prepare_setup_context(self, analysis: Dict[str, Any]) -> str:
        """Prepare context for setup documentation."""
        return f"""
Repository Analysis for Setup Documentation:
- Project Type: {analysis.get('project_type', 'Unknown')}
- Dependencies: {', '.join(analysis.get('dependencies', []))}
- Config Files: {', '.join(analysis.get('config_files', []))}

Detail Level: {self.detail_level}

Generate detailed setup and installation documentation.
"""
    
    def _get_setup_system_prompt(self) -> str:
        """Get system prompt for setup documentation."""
        return """You are an expert DevOps engineer creating setup documentation.

Create comprehensive setup documentation that includes:
1. Prerequisites and system requirements
2. Installation steps
3. Configuration setup
4. Environment variables
5. Database setup (if applicable)
6. Testing the installation
7. Troubleshooting common issues

Provide step-by-step instructions that are easy to follow."""
    
    def _prepare_usage_context(self, analysis: Dict[str, Any]) -> str:
        """Prepare context for usage documentation."""
        return f"""
Repository Analysis for Usage Documentation:
- Project Type: {analysis.get('project_type', 'Unknown')}
- Main Files: {', '.join(analysis.get('main_files', []))}
- Languages: {', '.join(analysis.get('languages', []))}

Detail Level: {self.detail_level}

Generate comprehensive usage documentation with examples and best practices.
"""
    
    def _get_usage_system_prompt(self) -> str:
        """Get system prompt for usage documentation."""
        return """You are an expert software developer creating usage documentation.

Create comprehensive usage documentation that includes:
1. Getting started guide
2. Basic usage examples
3. Advanced features and configurations
4. Best practices and patterns
5. Common use cases
6. Performance optimization tips
7. Integration examples

Provide practical examples and real-world scenarios."""


class DocumentationBot:
    """Main class that orchestrates the documentation generation process."""
    
    def __init__(self, repo_path: str, detail_level: str = "medium", max_llm_calls: int = 20):
        """Initialize the documentation bot."""
        self.repo_path = Path(repo_path)
        self.detail_level = detail_level
        self.max_llm_calls = max_llm_calls
        
        # Validate inputs
        if not self.repo_path.exists():
            raise ValueError(f"Repository path does not exist: {repo_path}")
        
        if detail_level not in ["low", "medium", "high"]:
            raise ValueError("Detail level must be 'low', 'medium', or 'high'")
        
        if max_llm_calls <= 0:
            raise ValueError("Max LLM calls must be positive")
        
        # Initialize analyzer (doesn't require OpenAI)
        self.analyzer = RepositoryAnalyzer(self.repo_path)
        # Initialize generator only when needed
        self.generator = None
    
    def _get_generator(self):
        """Get or create the DocumentationGenerator instance."""
        if self.generator is None:
            self.generator = DocumentationGenerator(self.repo_path, self.detail_level, self.max_llm_calls)
        return self.generator
    
    def generate_documentation(self) -> None:
        """Generate comprehensive documentation for the repository."""
        logger.info(f"Starting documentation generation for: {self.repo_path}")
        logger.info(f"Detail level: {self.detail_level}, Max LLM calls: {self.max_llm_calls}")
        
        try:
            # Step 1: Analyze the repository
            analysis = self.analyzer.analyze()
            logger.info(f"Repository analysis complete. Found {len(analysis['structure'])} files.")
            
            # Step 2: Generate README.md if it doesn't exist
            readme_path = self.repo_path / "README.md"
            if not readme_path.exists():
                generator = self._get_generator()
                generator.generate_readme(analysis)
            else:
                logger.info("README.md already exists, skipping generation.")
            
            # Step 3: Generate comprehensive documentation
            generator = self._get_generator()
            generator.generate_documentation_files(analysis)
            
            logger.info("Documentation generation complete!")
            logger.info(f"Total LLM calls made: {generator.llm_calls_made}")
            
        except Exception as e:
            logger.error(f"Error during documentation generation: {e}")
            raise


def main():
    """Main entry point for the command-line interface."""
    parser = argparse.ArgumentParser(
        description="Generate comprehensive documentation for a code repository"
    )
    parser.add_argument(
        "--repo-path",
        required=True,
        help="Path to the repository to document"
    )
    parser.add_argument(
        "--detail-level",
        choices=["low", "medium", "high"],
        default="medium",
        help="Level of detail for documentation (default: medium)"
    )
    parser.add_argument(
        "--max-llm-calls",
        type=int,
        default=20,
        help="Maximum number of LLM API calls (default: 20)"
    )
    
    args = parser.parse_args()
    
    try:
        bot = DocumentationBot(
            repo_path=args.repo_path,
            detail_level=args.detail_level,
            max_llm_calls=args.max_llm_calls
        )
        bot.generate_documentation()
        
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 