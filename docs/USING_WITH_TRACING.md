# Using TradingAgents with Phoenix Tracing

This guide walks you through using TradingAgents with Phoenix tracing enabled, from setup to viewing and analyzing traces.

## Prerequisites

1. **Docker installed** and running
2. **Python 3.10+** (3.13 recommended)
3. **API keys** configured:
   ```bash
   export FINNHUB_API_KEY=your_finnhub_key
   export OPENAI_API_KEY=your_openai_key
   ```

## Setup Phoenix

### Step 1: Start Phoenix Container

```bash
# Start Phoenix in background
docker-compose up -d

# Verify it's running
docker-compose ps
```

Expected output:
```
NAME                    STATUS    PORTS
tradingagents-phoenix   Up        0.0.0.0:6006->6006/tcp, ...
```

### Step 2: Verify Phoenix UI

Open your browser to **http://localhost:6006/**

You should see the Phoenix dashboard with no traces yet.

### Step 3: Install Dependencies

If you haven't already:

```bash
pip install -r requirements.txt
```

This installs OpenTelemetry packages needed for tracing.

## Basic Usage

### Simple Example with Tracing

Create a file `test_tracing.py`:

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# Configure
config = DEFAULT_CONFIG.copy()
config["phoenix_tracing"] = True  # Enable tracing
config["deep_think_llm"] = "o4-mini"
config["quick_think_llm"] = "gpt-4o-mini"
config["max_debate_rounds"] = 1

# Run analysis
ta = TradingAgentsGraph(debug=True, config=config)
try:
    print("Analyzing NVDA...")
    _, decision = ta.propagate("NVDA", "2024-05-10")
    print(f"\nDecision: {decision}")
    print("\nView traces at: http://localhost:6006/")
finally:
    ta.cleanup()
```

## CLI Usage with Tracing

### Option 1: Environment Variables

```bash
# Enable tracing via environment variable
export PHOENIX_TRACING=true
export PHOENIX_PROJECT=my-analysis

# Run CLI
python -m cli.main
```

### Option 2: Modify CLI Code

Edit your script to enable tracing:

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# Get user selections (ticker, date, etc.)
selections = get_user_selections()

# Configure with tracing
config = DEFAULT_CONFIG.copy()
config["phoenix_tracing"] = True  # Add this line
config["max_debate_rounds"] = selections["research_depth"]
# ... other config

# Initialize with tracing
graph = TradingAgentsGraph(
    selected_analysts=[analyst.value for analyst in selections["analysts"]],
    config=config,
    debug=True
)

# Run and view traces
try:
    _, decision = graph.propagate(selections["ticker"], selections["date"])
finally:
    graph.cleanup()
```

## Programmatic Usage

### Basic Example

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

config = DEFAULT_CONFIG.copy()
config["phoenix_tracing"] = True

ta = TradingAgentsGraph(debug=True, config=config)
try:
    _, decision = ta.propagate("AAPL", "2024-05-10")
finally:
    ta.cleanup()
```

### With Custom Configuration

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

config = DEFAULT_CONFIG.copy()

# Tracing settings
config["phoenix_tracing"] = True
config["phoenix_project"] = "aapl-analysis"
config["phoenix_collector_endpoint"] = "http://localhost:4317"

# Model settings
config["deep_think_llm"] = "o4-mini"
config["quick_think_llm"] = "gpt-4o-mini"

# Analysis settings
config["max_debate_rounds"] = 2  # More thorough analysis
config["online_tools"] = True

# Select specific analysts
selected_analysts = ["market", "news", "fundamentals"]

ta = TradingAgentsGraph(
    selected_analysts=selected_analysts,
    debug=True,
    config=config
)

try:
    _, decision = ta.propagate("AAPL", "2024-05-10")
    print(f"Decision: {decision}")
finally:
    ta.cleanup()
```

### Multiple Analyses with Tracing

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

tickers = ["NVDA", "AAPL", "TSLA", "MSFT"]
dates = ["2024-05-10", "2024-05-11", "2024-05-12"]

config = DEFAULT_CONFIG.copy()
config["phoenix_tracing"] = True
config["phoenix_project"] = "multi-ticker-analysis"
config["deep_think_llm"] = "o4-mini"
config["quick_think_llm"] = "gpt-4o-mini"
config["max_debate_rounds"] = 1

ta = TradingAgentsGraph(debug=False, config=config)  # debug=False for cleaner output

try:
    for ticker in tickers:
        for date in dates:
            print(f"\nAnalyzing {ticker} on {date}...")
            _, decision = ta.propagate(ticker, date)
            print(f"Decision: {decision}")
finally:
    ta.cleanup()

print("\nView all traces at: http://localhost:6006/")
```

## Viewing Traces

### Accessing Phoenix UI

1. Open **http://localhost:6006/** in your browser
2. You'll see the main dashboard

### Understanding the UI

#### Main Dashboard
- **Traces**: List of all execution traces
- **Projects**: Filter by project name
- **Timeline**: Time-based view of traces
- **Search**: Find specific traces

#### Trace Details

Click on any trace to see:

1. **Execution Graph**: Visual flow of agent execution
   - Nodes: Each agent and LLM call
   - Edges: Data flow between agents
   - Colors: Status (success, error, pending)

2. **Span Details**: Click any node to see:
   - **Input**: What was sent to the agent/LLM
   - **Output**: What the agent/LLM returned
   - **Metadata**: Ticker, date, project info
   - **Timing**: Duration and timestamps
   - **Tokens**: Token usage for LLM calls

3. **LLM Calls**: Special section for language model interactions
   - **Prompts**: Full prompts sent to models
   - **Responses**: Complete model responses
   - **Token Usage**: Input/output token counts
   - **Cost**: Estimated API costs

### Filtering and Searching

Use the search bar to filter traces:

```
# Find traces for specific ticker
ticker:NVDA

# Find traces from specific date
date:2024-05-10

# Find traces by project
project:my-analysis

# Combine filters
ticker:AAPL AND date:2024-05-10
```

### Analyzing Agent Execution

Look for these key insights:

1. **Agent Flow**: Which agents were activated
   ```
   Market Analyst → Social Analyst → News Analyst →
   Bull Researcher → Bear Researcher → Research Manager →
   Trader → Risk Analysts → Portfolio Manager
   ```

2. **Debate Rounds**: How many rounds of debate occurred
   - Bull/Bear debate iterations
   - Risk analysis discussions

3. **Decision Points**: Key decision-making moments
   - Research Manager's synthesis
   - Trader's investment plan
   - Risk Manager's assessment
   - Portfolio Manager's final decision

4. **Tool Usage**: What data sources were accessed
   - YFinance data fetches
   - Finnhub API calls
   - Google News queries
   - Reddit sentiment analysis

5. **Performance**: Identify bottlenecks
   - Which agents took longest
   - Which LLM calls were slowest
   - Which data fetches were delayed
