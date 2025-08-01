# Documentation Bot

An agentic system that automatically generates comprehensive documentation for code repositories using OpenAI's language models.

## Features

- **Intelligent Repository Analysis**: Automatically analyzes repository structure, file types, and dependencies
- **Comprehensive Documentation**: Generates README.md and detailed documentation in `/docs` directory
- **Configurable Detail Levels**: Choose between low, medium, and high detail documentation
- **Cost Control**: Limit the number of LLM API calls to control costs
- **Multiple Documentation Types**: Creates architecture, API, setup, and usage documentation
- **Smart File Filtering**: Ignores binary files, large files, and common directories

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd documentation-bot
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

## Configuration

Create a `.env` file with the following variables:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4
```

## Usage

### Basic Usage

```bash
python documentation_bot.py --repo-path /path/to/your/repository
```

### Advanced Usage

```bash
python documentation_bot.py \
  --repo-path /path/to/your/repository \
  --detail-level high \
  --max-llm-calls 30
```

### Command Line Arguments

- `--repo-path`: Path to the repository to document (required)
- `--detail-level`: Level of detail for documentation (`low`, `medium`, `high`, default: `medium`)
- `--max-llm-calls`: Maximum number of LLM API calls (default: 20)

### Detail Levels

- **Low**: Basic overview with minimal technical details
- **Medium**: Setup instructions, basic usage, and key features
- **High**: Detailed setup instructions, code examples, architecture overview, and comprehensive feature documentation

## Output

The bot generates the following documentation:

1. **README.md** (if it doesn't exist): Main project documentation
2. **/docs/architecture.md**: System architecture and design
3. **/docs/api.md**: API documentation and endpoints
4. **/docs/setup.md**: Installation and setup instructions
5. **/docs/usage.md**: Usage examples and best practices

## Architecture

The system consists of three main components:

### RepositoryAnalyzer
- Analyzes repository structure and content
- Identifies file types, languages, and dependencies
- Filters out binary files and irrelevant directories

### DocumentationGenerator
- Generates documentation using OpenAI's language models
- Manages LLM API calls and cost control
- Creates different types of documentation based on analysis

### DocumentationBot
- Orchestrates the entire documentation generation process
- Handles command-line interface and error management

## Testing

Run the test suite:

```bash
python -m pytest test_documentation_bot.py -v
```

Or run with unittest:

```bash
python test_documentation_bot.py
```

## Examples

### Example 1: Python Flask Application

```bash
python documentation_bot.py \
  --repo-path /path/to/flask-app \
  --detail-level high \
  --max-llm-calls 25
```

This will generate:
- Comprehensive README with Flask-specific setup instructions
- Architecture documentation with Flask patterns
- API documentation for Flask routes
- Detailed setup guide with virtual environment instructions

### Example 2: JavaScript React Application

```bash
python documentation_bot.py \
  --repo-path /path/to/react-app \
  --detail-level medium \
  --max-llm-calls 15
```

This will generate:
- README with React-specific information
- Component architecture documentation
- Setup guide for npm/yarn installation
- Usage examples for React components

## Cost Management

The bot uses OpenAI's API, which incurs costs based on:
- Number of API calls made
- Model used (GPT-4 is more expensive than GPT-3.5-turbo)
- Length of generated content

To control costs:
1. Set a reasonable `--max-llm-calls` limit
2. Use `--detail-level low` for basic documentation
3. Monitor your OpenAI API usage

## Limitations

- Requires OpenAI API key and internet connection
- Limited to text-based files (ignores images, videos, etc.)
- Maximum file size of 1MB per file
- Documentation quality depends on the LLM model used

## Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Implement your changes
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check the existing documentation
2. Review the test cases for usage examples
3. Open an issue on GitHub

## Roadmap

- [ ] Support for more programming languages
- [ ] Integration with other LLM providers
- [ ] Custom documentation templates
- [ ] Incremental documentation updates
- [ ] Documentation quality scoring
- [ ] Integration with CI/CD pipelines 