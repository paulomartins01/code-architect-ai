# 🏗️ CodeArchitect AI

> Transform your React Native codebase into an intelligent knowledge base for AI-powered architectural decisions

## 🎯 Overview

**CodeArchitect AI** uses RAG (Retrieval Augmented Generation) to analyze your codebase and create an intelligent agent (default name: **Cortex**) that understands your code deeply and provides architectural guidance based on actual code structure, patterns, and best practices.

The agent name is configurable in `config/default.yaml`.

## ✨ Features

- 🔍 **Smart Code Analysis**: Automatically analyzes React Native projects
- 🧠 **RAG-Powered**: Uses Retrieval Augmented Generation for context-aware responses
- 📊 **Architecture Detection**: Identifies layers, patterns, and dependencies
- 🎨 **Flexible Configuration**: YAML-based configuration for easy customization
- 📦 **Export Ready**: Generates vector databases compatible with agent builders
- 💰 **Dual Embedding Support**: Choose between FREE local embeddings or OpenAI

## 🚀 Quick Start

### Installation

**Option 1: Local Embeddings (FREE, recommended)**

```bash
pip install -r requirements-local.txt
# No API key needed!
```

**Option 2: OpenAI Embeddings (Better quality)**

```bash
pip install -r requirements-openai.txt
# Setup .env with OPENAI_API_KEY
```

**Option 3: Both options**

```bash
pip install -r requirements.txt
```

### Basic Usage

```bash
# Run with default configuration (uses LOCAL embeddings)
python main.py --source ../your-react-native-project

# Dry run (no embeddings, just analysis)
python main.py --dry-run

# Use OpenAI instead
python main.py --config config/openai.yaml --source ../your-project
```

## 🔄 Embedding Options

### Local Embeddings (Default) 🆓

**Pros:**

- ✅ Completely FREE
- ✅ No API key needed
- ✅ Works offline
- ✅ Good quality (90% of OpenAI)

**Cons:**

- ⏱️ Slower (depends on your hardware)
- 💾 First run downloads model (~80MB)

```yaml
# config/default.yaml (already configured)
embedding:
  provider: "local"
  model: "all-MiniLM-L6-v2"
  batch_size: 32
  cache_folder: "./models"
```

### OpenAI Embeddings ☁️

**Pros:**

- ✅ Best quality (100%)
- ✅ Fast (~2-3 min for 500 files)
- ✅ Lower memory usage

**Cons:**

- 💰 Costs money (~$0.02-0.10 per project)
- 🔑 Requires API key
- 🌐 Needs internet

```bash
# Setup
echo "OPENAI_API_KEY=sk-xxx" > .env

# Edit config/default.yaml
embedding:
  provider: "openai"
  model: "text-embedding-3-small"
  batch_size: 100
```

### Comparison

| Aspect      | Local      | OpenAI      |
| ----------- | ---------- | ----------- |
| **Cost**    | FREE       | ~$0.02-0.10 |
| **API Key** | Not needed | Required    |
| **Quality** | 89-92%     | 95-100%     |
| **Speed**   | 5 min      | 2 min       |
| **Offline** | ✅ Yes     | ❌ No       |

## ⚙️ Configuration

Edit `config/default.yaml` to customize:

```yaml
paths:
  source_code: "./your-project"

code_processing:
  extensions: [".js", ".jsx", ".ts", ".tsx"]
  ignore_dirs: ["node_modules", ".git", "build"]

# Choose your embedding provider
embedding:
  provider: "local" # or "openai"
  model: "all-MiniLM-L6-v2" # or "text-embedding-3-small"
```

## 📖 Usage Flow

### 1. Configure

Edit `config/default.yaml` with your project path

### 2. Run

```bash
python main.py --source ../my-react-native-app
```

### 3. Upload

Upload `output/cortex_knowledge_base.json` to your agent builder

### 4. Use

Start asking architectural questions to your agent!

## 🤖 Example Agent Queries

- "What's our current architecture structure?"
- "How is navigation implemented?"
- "Suggest improvements for state management"
- "Review the authentication flow"
- "What patterns are being used?"

## 📊 Output Files

- `cortex_knowledge_base.json` - Vector database for agent
- `cortex_summary.md` - Human-readable summary with statistics
- `cortex.log` - Processing logs

## 🎯 Available Models

### Local Models

1. **all-MiniLM-L6-v2** ⭐ (Default)

   - Fast, good quality
   - 384 dimensions
   - 80MB download

2. **all-mpnet-base-v2**

   - Best quality
   - 768 dimensions
   - 420MB download

3. **paraphrase-multilingual-MiniLM-L12-v2**
   - Multilingual (great for PT-BR comments)
   - 384 dimensions
   - 420MB download

### OpenAI Models

1. **text-embedding-3-small** ⭐ (Recommended)

   - $0.02 per 1M tokens
   - 1536 dimensions
   - Best value

2. **text-embedding-3-large**
   - $0.13 per 1M tokens
   - 3072 dimensions
   - Maximum quality

## 🛠️ Advanced Options

```bash
# Skip embeddings (faster, for testing structure)
python main.py --skip-embeddings

# Custom output location
python main.py --output ./custom/path/knowledge_base.json

# Use specific config
python main.py --config config/local.yaml --source ../project
python main.py --config config/openai.yaml --source ../project
```

## 🐛 Troubleshooting

### "No module named 'sentence_transformers'"

```bash
pip install sentence-transformers torch
```

### "OPENAI_API_KEY not found"

```bash
# Option 1: Create .env file
echo "OPENAI_API_KEY=sk-xxx" > .env

# Option 2: Use local embeddings
# Edit config/default.yaml: provider: "local"
```

### "CUDA out of memory"

```yaml
# Reduce batch size in config
embedding:
  batch_size: 16 # reduce from 32
```

Or force CPU:

```bash
# Add to .env
FORCE_CPU=true
```

## 📋 Project Structure

```
code-architect-ai/
├── config/                 # Configuration files
│   ├── default.yaml        # Main config (local by default)
│   ├── local.yaml          # Local embeddings config
│   ├── openai.yaml         # OpenAI embeddings config
│   └── config_schema.py    # Configuration schema
├── src/
│   ├── core/               # Core processing modules
│   │   ├── vectorizer.py           # Main engine (supports both)
│   │   ├── local_embeddings.py     # Local embeddings
│   │   ├── code_analyzer.py        # Code analysis
│   │   └── chunk_strategy.py       # Smart chunking
│   ├── exporters/          # Export modules
│   │   └── vector_exporter.py
│   └── utils/              # Utility modules
│       ├── logger.py
│       └── file_utils.py
├── output/                 # Generated outputs
├── main.py                 # Main entry point
├── requirements.txt        # All dependencies
├── requirements-local.txt  # Local only
└── requirements-openai.txt # OpenAI only
```

## 🎨 Key Features

### Smart Chunking

Respects code structure - doesn't break in the middle of functions

### Rich Metadata

Extracts components, hooks, imports, exports, patterns

### Layer Detection

Automatically identifies architectural layers (presentation/business/data)

### Feature Mapping

Detects features by folder structure

### Pattern Recognition

Identifies Redux, Context API, Navigation, StyleSheets, API calls, etc.

### Complexity Analysis

Calculates complexity (low/medium/high)

### Hardware Detection (Local)

Automatically uses GPU if available (CUDA, MPS, or CPU)

### Beautiful Logs

Clear formatting with emojis and progress tracking

### Summary Report

Generates markdown report with statistics

## 📈 Performance Expectations

For a medium project (500 files, 3000 chunks):

**Local (all-MiniLM-L6-v2)**

- Time: ~5 minutes
- Cost: $0
- RAM: ~2GB
- Quality: 90%

**OpenAI (text-embedding-3-small)**

- Time: ~2 minutes
- Cost: ~$0.10
- RAM: ~500MB
- Quality: 95-100%

## 🔄 Switching Between Providers

### From Local to OpenAI

```bash
pip install openai tiktoken
echo "OPENAI_API_KEY=sk-xxx" > .env
# Edit config/default.yaml: provider: "openai"
python main.py --source ../project
```

### From OpenAI to Local

```bash
pip install sentence-transformers torch
# Edit config/default.yaml: provider: "local"
python main.py --source ../project  # No API key needed!
```

## 🚨 Important Notes

- **First run (local)**: Downloads model (~80MB), subsequent runs are fast
- **Rate limits (OpenAI)**: Code handles rate limits with retry logic
- **Encoding**: Handles utf-8 and latin-1 automatically
- **Validation**: Validates source_code path exists before processing
- **Error handling**: Captures errors per file, doesn't stop entire process

## 💡 Recommendations

### Getting Started

👉 **Use LOCAL embeddings**

- Free and works great
- No configuration hassle
- Perfect for testing and development

### Production/Critical Projects

👉 **Use OpenAI if:**

- You need maximum quality
- Budget is available
- Speed is critical
- Project is mission-critical

### Best Practice

👉 **Use both:**

- Develop with local (free)
- Deploy to production with OpenAI (quality)
- Compare results to validate

## ⚙️ Agent Configuration

You can customize the agent name in `config/default.yaml`:

```yaml
project:
  agent_name: "Cortex" # Change to your preferred name
```

The agent name appears in:

- Generated knowledge base metadata
- Summary reports
- Log messages

## 📝 License

MIT License

## 🙏 Credits

Made with ❤️ for better software architecture decisions

---

**CodeArchitect AI** - Empowering architectural decisions with AI 🏗️

_Now with FREE local embeddings option!_
