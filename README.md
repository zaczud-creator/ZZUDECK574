# Pipeline Audit Agent

An agentic AI application that audits game studio production pipelines and generates prioritized optimization recommendations. Built with Claude's API and tool use to demonstrate how an AI agent can reason through complex, multi-step analysis.

## How It Works

The agent follows a structured analysis workflow, visible step-by-step in the terminal:

```
┌──────────────────────────────────────────────────────────────┐
│  Step 1 → Read pipeline config, identify bottlenecks         │
│  Step 2 → Look up industry benchmarks for each area          │
│  Step 3 → Estimate cost savings from AI automation           │
│  Step 4 → Assess implementation complexity                   │
│  Step 5 → Generate prioritized action plan                   │
└──────────────────────────────────────────────────────────────┘
```

At each step, the agent's chain-of-thought reasoning is displayed, so you can see *why* it makes each decision — not just the final output.

## Architecture: Agentic Tool Use

This project demonstrates **agentic tool use** — a pattern where the AI model drives the workflow by deciding which tools to call and in what order, rather than following a hardcoded script.

```
User Input (pipeline JSON)
       │
       ▼
┌─────────────────────┐
│   Claude (Agent)     │ ◄── System prompt with audit instructions
│                     │
│  Reasoning loop:    │
│  1. Analyze config  │
│  2. Decide next     │──── Tool call ──► lookup_benchmark()
│     tool to call    │◄─── Result ──────┘
│  3. Interpret       │
│     results         │──── Tool call ──► estimate_savings()
│  4. Decide next     │◄─── Result ──────┘
│     step            │
│  5. Repeat until    │──── Tool call ──► assess_complexity()
│     analysis is     │◄─── Result ──────┘
│     complete        │
│  6. Synthesize      │──── Tool call ──► generate_recommendation()
│     findings        │◄─── Result ──────┘
└─────────────────────┘
       │
       ▼
  Structured Report
```

### Why Agentic?

Traditional automation scripts follow rigid, predefined paths. The agentic approach is different:

- **Claude decides** which pipeline areas to investigate based on the data it sees
- **Claude decides** how many bottlenecks to analyze (3–5, depending on what it finds)
- **Claude reasons** about which benchmarks are most relevant to each studio's situation
- **Claude adapts** its analysis based on studio size, tools, and team structure

The same agent produces meaningfully different analyses for an indie studio vs. a AAA publisher — not because of branching `if/else` logic, but because the AI reasons about each situation differently.

## The Tools

Four tools are defined as Python functions that Claude can invoke:

| Tool | Purpose | Example Use |
|------|---------|-------------|
| `lookup_benchmark(category)` | Returns industry benchmark data | Compare a studio's QA hours against industry average |
| `estimate_savings(current_hours, ai_reduction_pct, hourly_rate)` | Calculates financial impact | Project annual savings from automating localization |
| `assess_complexity(tool_category, current_stack)` | Rates implementation difficulty | How hard is it to add AI to a Jenkins-based CI/CD pipeline? |
| `generate_recommendation(bottleneck, benchmark_data, savings)` | Formats a structured recommendation | Create a prioritized action item with severity rating |

These tools use simulated data (hardcoded benchmarks and heuristics). In a production system, they would connect to real databases, vendor APIs, and historical project data.

## Quick Start

### Prerequisites

- Python 3.11+
- An Anthropic API key

### Setup

```bash
# Clone / navigate to the project
cd pipeline-auditor

# Install the Anthropic SDK
pip install anthropic

# Set your API key
export ANTHROPIC_API_KEY=your-key-here
```

### Run

```bash
# Interactive mode — choose from example studios
python agent.py

# Direct mode — specify a pipeline file
python agent.py pipeline_examples/indie_studio.json

# Save a JSON report alongside the terminal output
python agent.py pipeline_examples/aaa_publisher.json --json-output report.json
```

## Example Studios

Three example pipeline configurations are included:

| File | Studio | Size | Team | Description |
|------|--------|------|------|-------------|
| `indie_studio.json` | Pixel Forge Games | Indie | 12 | Solo QA tester, no CI/CD, Google Sheets localization |
| `mid_size_studio.json` | Horizon Interactive | Mid-size | 85 | Live-service studio, partial automation, multi-platform |
| `aaa_publisher.json` | Titan Entertainment Group | AAA | 450 | 4 active titles, proprietary engine, 15 languages |

### Creating Your Own

Create a JSON file with this structure:

```json
{
  "studio_name": "Your Studio",
  "studio_size": "indie|mid-size|AAA",
  "team_size": 50,
  "active_projects": 2,
  "team_structure": { "developers": 20, "artists": 15, ... },
  "tools": { "engine": "Unity", "ci_cd": "GitHub Actions", ... },
  "qa_process": { "hours_per_week": 200, "automation_pct": 30, ... },
  "localization": { "languages": [...], "turnaround_days": 10, ... },
  "asset_creation": { "assets_per_artist_per_week": 8, ... },
  "deployment": { "build_time_minutes": 60, "deploys_per_week": 5, ... },
  "hourly_rates": { "developer": 75, "artist": 60, "average": 65 }
}
```

## Project Structure

```
pipeline-auditor/
├── agent.py                  # Main agentic loop — Claude API with tool use
├── tools.py                  # Tool definitions (schemas) and implementations
├── report.py                 # Terminal report formatting and JSON export
├── README.md                 # This file
└── pipeline_examples/
    ├── indie_studio.json     # Pixel Forge Games — 12-person indie team
    ├── mid_size_studio.json  # Horizon Interactive — 85-person live-service
    └── aaa_publisher.json    # Titan Entertainment — 450-person AAA publisher
```

## How Tool Use Works (Technical Detail)

Claude's tool use follows a request-response loop:

1. **We define tools** as JSON schemas in `TOOL_DEFINITIONS` (see `tools.py`). Each schema describes the tool's name, purpose, and expected parameters.

2. **We send a message** to Claude with the tools attached. Claude's response may contain `tool_use` content blocks — structured requests to call specific tools with specific arguments.

3. **We execute the tool** locally in Python using `execute_tool()`, which dispatches to the matching function.

4. **We send the result back** to Claude as a `tool_result` message. Claude then reasons about the result and decides whether to call another tool or produce its final answer.

5. **The loop continues** until Claude responds with `stop_reason: "end_turn"`, indicating it's finished its analysis.

This is the same pattern used in production agentic systems — Claude drives the workflow, the application provides the tools, and the loop runs until the task is complete.

```python
# Simplified version of the core loop in agent.py
while True:
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        tools=TOOL_DEFINITIONS,
        messages=messages,
    )

    for block in response.content:
        if block.type == "tool_use":
            result = execute_tool(block.name, block.input)
            # Send result back to Claude...

    if response.stop_reason == "end_turn":
        break  # Agent is done
```
