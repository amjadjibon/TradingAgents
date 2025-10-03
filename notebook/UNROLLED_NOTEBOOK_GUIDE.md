# TradingAgents Unrolled Notebook Guide

## Overview

The `trading_agents_unrolled.ipynb` notebook demonstrates **manual unrolling** of the TradingAgents LangGraph workflow. Instead of letting LangGraph automatically execute the multi-agent pipeline, we manually execute each node step-by-step in Jupyter cells.

This approach provides:
- **Full visibility** into each agent's execution
- **Step-by-step debugging** capabilities
- **Interactive experimentation** with individual agents
- **Manual flow control** for research and development

## What is Graph Unrolling?

### Standard LangGraph Execution

Normally, TradingAgents uses LangGraph's automatic execution:

```python
graph = trading_graph.compile()
result = graph.invoke(initial_state)  # Automatically runs all nodes
```

LangGraph internally:
1. Manages state transitions
2. Routes between nodes based on conditional logic
3. Handles tool execution loops
4. Cleans up messages between agents

### Unrolled Execution

In the unrolled notebook, we manually perform each step:

```python
# Manual node execution
state = executor.create_node_input("market_analyst")
result = market_analyst(state)
executor.update_state(result)

# Manual tool execution
if result.tool_calls:
    tool_result = market_tools.invoke(state)
    executor.update_state(tool_result)

# Manual message cleanup
# ... (clear messages)
```

This gives you **granular control** over every step in the workflow.

## Architecture

### 1. State Management with LangGraph Channels

The core of unrolling is the `TradingAgentsExecutor` class, which uses LangGraph's internal channel system:

```python
class TradingAgentsExecutor:
    def __init__(self):
        # Create StateGraph to get official channels
        temp_builder = StateGraph(AgentState)
        temp_builder._add_schema(AgentState)

        # Extract real channels from StateGraph
        self.channels = temp_builder.channels.copy()

        # Initialize channels
        for channel in self.channels.values():
            channel.update([])
```

**Key Components:**

- **Channels**: LangGraph's state storage mechanism (similar to Redux stores)
- **Mapper**: Official state key mapper from LangGraph (`_pick_mapper`)
- **PregelNode**: LangGraph's node wrapper for state processing

### 2. Node Input Creation

Each node needs properly formatted input from the current state:

```python
def create_node_input(self, node_name: str) -> Dict[str, Any]:
    """Create input for a specific node using official _proc_input."""
    if node_name not in self.nodes:
        self.register_node(node_name)

    node = self.nodes[node_name]
    return _proc_input(
        proc=node,
        managed={},
        channels=self.channels,
        for_execution=True,
        scratchpad=None,
        input_cache=None
    )
```

This uses LangGraph's internal `_proc_input` function to extract the correct state for a node.

### 3. State Updates

After each node executes, we update the channels:

```python
def update_state(self, node_output: Dict[str, Any]):
    """Update channels with node output."""
    for key, value in node_output.items():
        if key in self.channels:
            channel = self.channels[key]
            channel_type = type(channel).__name__

            if channel_type == "LastValue":
                channel.update([value])
            elif channel_type == "BinaryOperatorAggregate":
                # Handle message aggregation
                if isinstance(value, list):
                    channel.update(value)
                else:
                    channel.update([value])
```

Different channel types require different update strategies:
- **LastValue**: Stores single values (e.g., `market_report`, `final_trade_decision`)
- **BinaryOperatorAggregate**: Aggregates lists (e.g., `messages` with `add_messages` reducer)

## Workflow Breakdown

### Phase 1: Analyst Nodes (Data Gathering)

Each analyst follows the same pattern:

```python
def run_analyst_with_tools(analyst_name, analyst_func, tool_node, executor):
    # 1. Get current state as input
    state = executor.create_node_input(analyst_name)

    # 2. Execute analyst (may request tools)
    result = analyst_func(state)
    executor.update_state(result)

    # 3. Check for tool calls
    current_state = executor.get_state()
    if current_state['messages'][-1].tool_calls:
        # Execute tools
        tool_result = tool_node.invoke(current_state)
        executor.update_state(tool_result)

        # Run analyst again with tool results
        state = executor.create_node_input(analyst_name)
        result = analyst_func(state)
        executor.update_state(result)

    # 4. Clear messages (critical step!)
    messages = current_state['messages']
    removal_operations = [RemoveMessage(id=m.id) for m in messages]
    placeholder = HumanMessage(content="Continue")
    executor.update_state({"messages": removal_operations + [placeholder]})
```

**Why Message Clearing is Critical:**

LangGraph's conditional logic checks `messages[-1].tool_calls` to route to tool nodes. Without clearing:
- Next analyst sees previous tool calls
- OpenAI API rejects with: "tool_calls must be followed by tool messages"
- Workflow breaks

### Phase 2: Research Debate (Bull vs Bear)

Manual debate loop with conditional routing:

```python
current_speaker = "bull"
debate_round = 0

while debate_round < config["max_debate_rounds"]:
    debate_round += 1
    state = executor.create_node_input(f"{current_speaker}_researcher")

    if current_speaker == "bull":
        result = bull_researcher(state)
        next_node = conditional_logic.should_continue_debate(result)
    else:
        result = bear_researcher(state)
        next_node = conditional_logic.should_continue_debate(result)

    executor.update_state(result)

    # Check if debate should end
    if next_node == "Research Manager":
        break

    # Switch speaker
    current_speaker = "bear" if current_speaker == "bull" else "bull"
```

**Conditional Logic:**

The `should_continue_debate()` function checks:
- Debate round count vs `max_debate_rounds`
- Returns `"Bear Researcher"` or `"Bull Researcher"` to continue
- Returns `"Research Manager"` to end debate

### Phase 3: Trader Node

Simple single execution (no tools, no debate):

```python
state = executor.create_node_input("trader")
result = trader(state)
executor.update_state(result)
```

### Phase 4: Risk Analysis Debate

Three-way debate with rotation:

```python
current_speaker = "risky"
while risk_round < config["max_risk_discuss_rounds"]:
    state = executor.create_node_input(f"{current_speaker}_analyst")

    if current_speaker == "risky":
        result = risky_analyst(state)
    elif current_speaker == "safe":
        result = safe_analyst(state)
    else:  # neutral
        result = neutral_analyst(state)

    next_node = conditional_logic.should_continue_risk_analysis(result)
    executor.update_state(result)

    if next_node == "Risk Judge":
        break

    # Rotate: risky -> safe -> neutral -> risky
    if current_speaker == "risky":
        current_speaker = "safe"
    elif current_speaker == "safe":
        current_speaker = "neutral"
    else:
        current_speaker = "risky"
```

### Phase 5: Final Decision

Risk manager synthesizes final decision:

```python
state = executor.create_node_input("risk_manager")
result = risk_manager(state)
executor.update_state(result)
```

## State Inspection

At any point, you can inspect the full state:

```python
current_state = executor.get_state()

# View individual reports
print(current_state['market_report'])
print(current_state['investment_debate_state']['bull_history'])

# View all messages
for msg in current_state['messages']:
    print(msg)
```

## Key Differences from Automatic Execution

| Aspect | Automatic (LangGraph) | Unrolled (Notebook) |
|--------|----------------------|---------------------|
| **Execution** | `graph.invoke()` runs all nodes | Manual cell-by-cell execution |
| **State Management** | Internal channel updates | Explicit `executor.update_state()` |
| **Tool Execution** | Automatic loop detection | Manual tool call checking |
| **Message Cleanup** | Automatic `msg_delete` nodes | Manual `RemoveMessage` operations |
| **Conditional Routing** | Graph edges and conditions | Manual if/else logic |
| **Debugging** | Limited visibility | Full visibility between steps |
| **Flexibility** | Fixed workflow | Can modify flow on-the-fly |

## Use Cases

### 1. Development & Debugging

```python
# Run just one analyst to test
state = run_analyst_with_tools("market_analyst", market_analyst, market_tools, executor)

# Inspect what happened
print(f"Tools called: {len(state['messages'][-2].tool_calls)}")
print(f"Report length: {len(state['market_report'])} chars")
```

### 2. Research & Experimentation

```python
# Try different debate strategies
config["max_debate_rounds"] = 5  # Increase rounds

# Or skip debate entirely
state = executor.create_node_input("research_manager")
result = research_manager(state)  # Direct to manager
```

### 3. A/B Testing Agents

```python
# Test two different market analysts
result_v1 = market_analyst_v1(state)
result_v2 = market_analyst_v2(state)

# Compare reports
print(f"V1 report: {result_v1['market_report'][:200]}")
print(f"V2 report: {result_v2['market_report'][:200]}")
```

### 4. Partial Execution

```python
# Run only analysts, skip trading decision
run_analyst_with_tools("market_analyst", market_analyst, market_tools, executor)
run_analyst_with_tools("news_analyst", news_analyst, news_tools, executor)

# Export analyst data without making trade decision
state = executor.get_state()
save_analyst_reports(state)
```

## Technical Deep Dive

### Channel Types in AgentState

```python
class AgentState(MessagesState):
    # LastValue channels (single value storage)
    company_of_interest: str
    trade_date: str
    sender: str
    market_report: str
    sentiment_report: str

    # BinaryOperatorAggregate (with add_messages reducer)
    messages: Annotated[list[BaseMessage], add_messages]

    # Nested state objects
    investment_debate_state: InvestDebateState
    risk_debate_state: RiskDebateState
```

### Message Flow Example

**Initial State:**
```python
messages = []
```

**After Market Analyst (with tool calls):**
```python
messages = [
    AIMessage(content="", tool_calls=[...]),  # Analyst requests tools
    ToolMessage(content="...", tool_call_id="..."),  # Tool 1 result
    ToolMessage(content="...", tool_call_id="..."),  # Tool 2 result
    AIMessage(content="Market report...")  # Final response
]
```

**After Message Cleanup:**
```python
messages = [
    HumanMessage(content="Continue")  # Placeholder for next agent
]
```

### Conditional Logic Implementation

```python
class ConditionalLogic:
    def should_continue_debate(self, state) -> str:
        debate_state = state.get("investment_debate_state", {})
        count = debate_state.get("count", 0)

        if count >= self.max_debate_rounds:
            return "Research Manager"

        # Determine next speaker based on current
        last_speaker = debate_state.get("latest_speaker", "")
        if last_speaker == "bull":
            return "Bear Researcher"
        else:
            return "Bull Researcher"
```

## Common Pitfalls & Solutions

### 1. Tool Call Mismatch Error

**Error:**
```
BadRequestError: tool_calls must be followed by tool messages
```

**Cause:** Messages not cleared between analysts

**Solution:** Always call message cleanup:
```python
removal_operations = [RemoveMessage(id=m.id) for m in messages]
executor.update_state({"messages": removal_operations + [placeholder]})
```

### 2. State Not Updating

**Issue:** Changes don't persist between cells

**Cause:** Not calling `executor.update_state()`

**Solution:**
```python
result = some_agent(state)
executor.update_state(result)  # Don't forget this!
```

### 3. Infinite Debate Loop

**Issue:** Debate never ends

**Cause:** Conditional logic not properly checked

**Solution:**
```python
if next_node == "Research Manager":
    break  # Must break the loop
```

## Advantages of Unrolled Execution

1. **Educational Value**: See exactly how multi-agent systems work
2. **Debugging Power**: Inspect state between every step
3. **Flexibility**: Modify workflow on-the-fly
4. **Research-Friendly**: Test individual components in isolation
5. **Transparency**: No hidden graph execution magic

## Limitations

1. **More Verbose**: Requires more code than `graph.invoke()`
2. **Manual Maintenance**: Must keep in sync with graph changes
3. **Error-Prone**: Easy to forget message cleanup or state updates
4. **No Auto-Retry**: Must implement error handling manually

## Comparison to Reference Notebook

The TradingAgents unrolled notebook follows the same pattern as the reference "Shortcut" notebook you provided:

**Similarities:**
- Uses `StateGraph` to extract official channels
- Uses `_proc_input` for node input creation
- Uses `_pick_mapper` for state mapping
- Manual state updates via channel operations
- PregelNode wrappers for execution

**Differences:**
- TradingAgents has more complex state (reports, debates)
- Multiple conditional routing points (debate loops)
- Tool execution patterns (analysts need tools)
- Message cleanup requirements (prevent tool_call errors)

## Conclusion

The unrolled notebook transforms TradingAgents from a "black box" graph execution into a **transparent, step-by-step workflow**. This is invaluable for:

- Understanding how multi-agent LLM systems work
- Debugging agent behavior
- Experimenting with different strategies
- Teaching and learning LangGraph internals

While less convenient than automatic execution, the unrolled approach provides **complete visibility and control** over the trading analysis pipeline.

---

## Quick Reference

### Execute Full Pipeline
```python
# Analysts
run_analyst_with_tools("market_analyst", market_analyst, market_tools, executor)
run_analyst_with_tools("social_analyst", social_analyst, social_tools, executor)
run_analyst_with_tools("news_analyst", news_analyst, news_tools, executor)
run_analyst_with_tools("fundamentals_analyst", fundamentals_analyst, fundamentals_tools, executor)

# Research debate (manual loop)
# ... (see notebook)

# Trader
state = executor.create_node_input("trader")
result = trader(state)
executor.update_state(result)

# Risk debate (manual loop)
# ... (see notebook)

# Final decision
state = executor.create_node_input("risk_manager")
result = risk_manager(state)
executor.update_state(result)
```

### Inspect State
```python
state = executor.get_state()
print(state['market_report'])
print(state['final_trade_decision'])
```

### Export Results
```python
import json
with open('state.json', 'w') as f:
    json.dump(state, f, indent=2)
```
