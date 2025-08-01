# Quick Start Guide

Get up and running with the Documentation Bot in minutes!

## Prerequisites

- Python 3.8 or higher
- OpenAI API key

## Installation

### Option 1: Clone and Install

```bash
# Clone the repository
git clone <repository-url>
cd documentation-bot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Option 2: Install via pip (when published)

```bash
pip install documentation-bot
```

## Configuration

1. **Set up your OpenAI API key**:
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

2. **Configure environment variables**:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   OPENAI_MODEL=gpt-4  # or gpt-3.5-turbo
   ```

## Usage

### Basic Usage

```bash
# Generate documentation for a repository
python documentation_bot.py --repo-path /path/to/your/repository
```

### Advanced Usage

```bash
# Generate high-detail documentation with cost control
python documentation_bot.py \
  --repo-path /path/to/your/repository \
  --detail-level high \
  --max-llm-calls 30
```

### Programmatic Usage

```python
from documentation_bot import DocumentationBot

# Initialize the bot
bot = DocumentationBot(
    repo_path="/path/to/your/repository",
    detail_level="medium",
    max_llm_calls=20
)

# Generate documentation
bot.generate_documentation()
```

## What You'll Get

The bot will generate:

1. **README.md** (if it doesn't exist)
2. **/docs/architecture.md** - System architecture documentation
3. **/docs/api.md** - API documentation
4. **/docs/setup.md** - Installation and setup guide
5. **/docs/usage.md** - Usage examples and best practices

## Detail Levels

- **Low**: Basic overview with minimal technical details
- **Medium**: Setup instructions, basic usage, and key features
- **High**: Detailed setup instructions, code examples, architecture overview

## Cost Management

- Set `--max-llm-calls` to control API usage
- Use `--detail-level low` for basic documentation
- Monitor your OpenAI API usage

## Examples

### Python Flask Application

```bash
python documentation_bot.py \
  --repo-path /path/to/flask-app \
  --detail-level high \
  --max-llm-calls 25
```

### JavaScript React Application

```bash
python documentation_bot.py \
  --repo-path /path/to/react-app \
  --detail-level medium \
  --max-llm-calls 15
```

## Testing

Run the test suite:

```bash
python test_basic.py
```

## Demo

See the system in action:

```bash
python demo.py
```

## Troubleshooting

### Common Issues

1. **"OpenAI library is not installed"**
   ```bash
   pip install openai
   ```

2. **"OPENAI_API_KEY environment variable is required"**
   - Make sure you've set up your `.env` file
   - Check that your API key is valid

3. **"Repository path does not exist"**
   - Verify the path to your repository is correct
   - Use absolute paths if needed

### Getting Help

- Check the main [README.md](README.md) for detailed documentation
- Review the test cases for usage examples
- Open an issue on GitHub for bugs or feature requests

## Next Steps

- Customize the documentation templates
- Integrate with CI/CD pipelines
- Add support for more programming languages
- Contribute to the project!

---

**Happy documenting! 📚** 