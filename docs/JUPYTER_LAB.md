# Jupyter Lab Setup Guide

This guide explains how to set up Jupyter Lab and run TradingAgents notebooks for interactive development and analysis.

## Table of Contents
- [Installation](#installation)
- [Running Notebooks](#running-notebooks)
- [Available Notebooks](#available-notebooks)
- [Troubleshooting](#troubleshooting)

## Installation

### Prerequisites
- Python 3.10+ (3.13 recommended)
- Virtual environment (conda or venv)
- TradingAgents dependencies installed

### Step 1: Create Virtual Environment

Using conda (recommended):
```bash
conda create -n tradingagents python=3.13
conda activate tradingagents
```

Or using venv:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### Step 2: Install TradingAgents Dependencies

```bash
# Install all project dependencies
pip install -r requirements.txt
```

### Step 3: Install Jupyter Lab

```bash
# Install Jupyter Lab
pip install jupyterlab

# Optional: Install useful extensions
pip install ipywidgets  # For interactive widgets
```

### Step 4: Set API Keys

Export required API keys as environment variables:

```bash
# Required for OpenAI models
export OPENAI_API_KEY=your_openai_key_here

# Optional: For Finnhub data (free tier available)
export FINNHUB_API_KEY=your_finnhub_key_here

# Optional: For Google Gemini models
export GOOGLE_API_KEY=your_google_key_here
```

**Note for Windows users:**
```cmd
set OPENAI_API_KEY=your_openai_key_here
set FINNHUB_API_KEY=your_finnhub_key_here
```

**Persistent API Keys (Optional):**

Add to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.):
```bash
export OPENAI_API_KEY=your_openai_key_here
export FINNHUB_API_KEY=your_finnhub_key_here
```

## Running Notebooks

### Launch Jupyter Lab

From the project root directory:

```bash
# Launch Jupyter Lab (opens in browser)
jupyter lab

# Or specify a specific notebook
jupyter lab notebook/trading_agents_demo.ipynb

# Launch on a specific port
jupyter lab --port=8889
```

Jupyter Lab will open in your default browser at `http://localhost:8888/` (or the port you specified).

### Running Notebooks Step-by-Step

1. **Navigate to the notebook**: In Jupyter Lab's file browser, navigate to `notebook/` directory

2. **Open a notebook**: Click on the notebook you want to run (e.g., `trading_agents_demo.ipynb`)

3. **Run cells sequentially**:
   - Click the "�" (Run) button for each cell
   - Or use keyboard shortcut: `Shift + Enter` to run cell and move to next
   - Or use `Ctrl + Enter` to run cell and stay on current cell

4. **Run all cells**:
   - Menu: `Run � Run All Cells`
   - Or keyboard shortcut: `Shift + Alt + Enter`

### Important: Cell Execution Order

**Always run cells in order from top to bottom**, especially for the first execution:

1. Imports and setup
2. Phoenix initialization
3. API key configuration
4. Tool definitions
5. Agent creation
6. Agent execution

If you get `NameError` (variable/function not defined), you likely skipped a cell. Go back and run the missing cells.

### Restarting the Kernel

If you encounter issues or want to start fresh:

1. **Restart kernel**: Menu � `Kernel � Restart Kernel`
2. **Restart and run all**: Menu � `Kernel � Restart Kernel and Run All Cells`
3. **Clear outputs**: Menu � `Edit � Clear All Outputs`

## Available Notebooks

### 1. `trading_agents_demo.ipynb`
**Purpose**: Demonstrate individual TradingAgents components with Phoenix tracing

**What it covers**:
- Market Analyst Agent (technical analysis)
- News Analyst Agent (sentiment analysis)
- Bull Researcher Agent (investment thesis)
- Phoenix tracing and observability
- Multi-ticker analysis

**Best for**: Learning agent architecture and debugging with Phoenix

**Run time**: ~5-10 minutes (depending on API latency)

**API costs**: Low (uses mock data, only LLM calls for analysis)

### 2. `agent.ipynb`
**Purpose**: Full TradingAgents multi-agent framework with Phoenix tracing

**What it covers**:
- Complete analyst team (market, news, social, fundamentals)
- Research team debate (bull vs bear)
- Trader agent (investment planning)
- Risk management team
- Portfolio manager (final decision)
- Memory and reflection system

**Best for**: Running complete trading analysis on real/historical data

**Run time**: ~15-30 minutes (full pipeline with multiple agents)

**API costs**: Higher (10+ agents, multiple debate rounds, tool calls)

### 3. `langchain_agent_tracing.ipynb`
**Purpose**: Example of LangChain agent tracing with Phoenix (reference implementation)

**What it covers**:
- Basic LangChain agent with tools
- Phoenix tracing setup
- Tool calling patterns
- Trace inspection

**Best for**: Understanding Phoenix integration patterns

## Troubleshooting

### Common Issues

#### 1. Module Not Found Error
```
ModuleNotFoundError: No module named 'tradingagents'
```

**Solution**: Make sure you're in the project root and the path is added:
```python
import sys
from pathlib import Path
project_root = Path.cwd().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
```

#### 2. API Key Not Set
```
openai.AuthenticationError: Invalid API key
```

**Solution**: Set your API key before running the notebook:
```bash
export OPENAI_API_KEY=your_key_here
```

Or set it in the notebook:
```python
import os
os.environ["OPENAI_API_KEY"] = "your_key_here"
```

#### 3. Variable/Function Not Defined
```
NameError: name 'news_analyst' is not defined
```

**Solution**: Run cells in order from the top. You likely skipped the cell that defines this variable.

#### 4. Phoenix UI Not Loading
```
Phoenix app running at http://localhost:6006/ but page won't load
```

**Solution**:
- Check if Phoenix is actually running: look for "<
 To view the Phoenix app..." message
- Try refreshing the page or opening in a different browser
- Check if port 6006 is already in use: `lsof -i :6006` (macOS/Linux)

#### 5. Kernel Dies/Crashes

**Solution**:
- Check memory usage (agents can be memory-intensive)
- Reduce batch size or number of concurrent analyses
- Restart kernel: `Kernel � Restart Kernel`

#### 6. Slow Notebook Performance

**Solution**:
- Use cheaper/faster models: `gpt-4o-mini` instead of `gpt-4o`
- Reduce debate rounds in config
- Clear old outputs: `Edit � Clear All Outputs`
- Close unused notebooks

### Phoenix Tracing Issues

#### Phoenix Already Running
If you see warnings about Phoenix already running:
```python
# Close existing session first
px.close_app()
# Then launch new session
session = px.launch_app()
```

#### Traces Not Appearing
1. Verify instrumentation is active:
   ```python
   tracer_provider = register()
   LangChainInstrumentor(tracer_provider=tracer_provider).instrument()
   ```

2. Check Phoenix session URL:
   ```python
   print(f"Phoenix UI: {session.url}")
   ```

3. Ensure agents are actually running (check for API calls in output)

## Best Practices

### 1. Development Workflow
```bash
# 1. Activate environment
conda activate tradingagents

# 2. Set API keys
export OPENAI_API_KEY=your_key_here

# 3. Launch Jupyter Lab
jupyter lab

# 4. Run notebook cells sequentially
# 5. View traces in Phoenix UI
# 6. Iterate and experiment
```

### 2. Cost Management

When developing/testing:
- Use `gpt-4o-mini` instead of `gpt-4o` (90% cheaper)
- Set `max_debate_rounds=1` to reduce iterations
- Use mock data in demo notebooks
- Monitor token usage in Phoenix UI

### 3. Saving Work

Jupyter Lab auto-saves, but you can also:
- **Manual save**: `Cmd/Ctrl + S` or `File � Save Notebook`
- **Export notebook**: `File � Export Notebook As � HTML/PDF`
- **Export as Python script**: `File � Export Notebook As � Executable Script`

### 4. Version Control

Add to `.gitignore`:
```gitignore
# Jupyter
.ipynb_checkpoints/
*/.ipynb_checkpoints/*

# Jupyter outputs (optional - remove if you want to commit outputs)
*.ipynb
!notebook/*.ipynb  # But keep notebooks in notebook/ directory
```

Commit notebooks without outputs:
```bash
# Clear all outputs before committing
jupyter nbconvert --clear-output --inplace notebook/*.ipynb
git add notebook/*.ipynb
git commit -m "Add clean notebooks"
```

## Additional Resources

- **Jupyter Lab Documentation**: https://jupyterlab.readthedocs.io/
- **Phoenix Tracing Docs**: https://arize.com/docs/phoenix/
- **LangChain Documentation**: https://python.langchain.com/
- **TradingAgents Project README**: [../CLAUDE.md](../CLAUDE.md)

## Tips & Tricks

### Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Run cell and select next | `Shift + Enter` |
| Run cell in place | `Ctrl + Enter` |
| Insert cell above | `A` |
| Insert cell below | `B` |
| Delete cell | `D D` (press D twice) |
| Change to Markdown | `M` |
| Change to Code | `Y` |
| Toggle line numbers | `Shift + L` |
| Command palette | `Cmd/Ctrl + Shift + C` |

### Magic Commands

```python
# Time cell execution
%time result = market_analyst(ticker, date)

# Time multiple runs
%timeit -n 10 market_analyst(ticker, date)

# Show environment variables
%env

# Set environment variable
%env OPENAI_API_KEY=your_key

# List all variables
%who

# Detailed variable info
%whos

# Load external Python file
%load file.py

# Run external Python file
%run script.py
```

### Debugging

```python
# Enable interactive debugger
%pdb on

# Insert breakpoint
import pdb; pdb.set_trace()

# Print all local variables
locals()

# Print detailed error traceback
import traceback
traceback.print_exc()
```

## Support

If you encounter issues not covered here:

1. Check the main project documentation: [../CLAUDE.md](../CLAUDE.md)
2. Review Phoenix setup guide: [../docs/PHOENIX_SETUP.md](PHOENIX_SETUP.md)
3. Open an issue: https://github.com/yourusername/TradingAgents/issues
