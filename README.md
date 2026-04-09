# Pipeline Audit Agent — Keywords Studios AI Consultancy Demo

An agentic AI application that audits game studio production pipelines and generates prioritized optimization recommendations mapped to Keywords Studios products and services. Built with Claude's API (Anthropic) and tool use to demonstrate the kind of analysis KWS AI Consultancy Solutions delivers to clients.

## Context: Why This Exists

Keywords Studios is the world's largest technical and creative services provider to the global video games industry — 70+ studios, 25+ countries, ~13,000 employees, serving 24 of the top 25 game publishers.

Keywords' **AI Consultancy Solutions** team helps game studios integrate AI into their production pipelines. This application demonstrates that methodology in action: an AI agent that reads a studio's pipeline configuration, benchmarks it against industry standards and KWS internal data, and produces a prioritized report recommending specific Keywords Studios products and services for each bottleneck.

The approach mirrors what Keywords learned through **Project KARA** — applied R&D remastering a game with AI-infused pipelines — and what the Consultancy team delivers through **Innovation-as-a-Service** engagements.

## How It Works

```
Studio Pipeline JSON ──> Claude (Agent) ──> Structured Audit Report
                              │
            ┌─────────────────┼─────────────────────────┐
            │                 │                         │
     lookup_benchmark   lookup_kws_solution      estimate_savings
     (industry data)    (KWS products/services)  (financial impact)
            │                 │                         │
            └────> assess_complexity ────> generate_recommendation
                   (difficulty + KWS         (prioritized action
                    solution mapping)         with severity rating)
```

### Step-by-step flow (visible in terminal):

1. **Read pipeline config** — Parse the studio's team structure, tools, QA process, localization workflow, asset pipeline, deployment, audio, player support, and trust & safety
2. **Benchmark against industry** — Compare metrics against industry averages, top-quartile performance, and KWS internal benchmarks (e.g., Mighty Build & Test coverage, KantanAI throughput, Project KARA timing data)
3. **Estimate cost savings** — Calculate financial impact with implementation cost ranges and months to ROI
4. **Assess complexity + map KWS solutions** — Rate implementation difficulty and identify the relevant Keywords Studios product (Mighty, KantanAI, Helpshift, Project KARA methodology, etc.) and division (Create, Globalize, Engage)
5. **Generate prioritized action plan** — Structured recommendations with severity ratings, a priority matrix, and recommended next steps (AI Workshop → Proof of Concept → Strategic Roadmap → Innovation-as-a-Service)

## The Tools (What the Agent Can Call)

| Tool | Purpose | KWS Relevance |
|------|---------|---------------|
| `lookup_benchmark(category)` | Industry benchmark data + KWS internal benchmarks | References Mighty, KantanAI, Helpshift, and Project KARA metrics |
| `lookup_kws_solution(category)` | Keywords Studios product/service for a pipeline area | Maps to specific KWS products, divisions, engagement models |
| `estimate_savings(hours, reduction%, rate)` | Financial impact with implementation costs | Tiered cost estimates based on project scale |
| `assess_complexity(category, stack)` | Implementation difficulty + KWS solution mapping | Considers current tools and KWS integration paths |
| `generate_recommendation(bottleneck, data, savings)` | Structured recommendation with severity rating | Formats actionable items with ROI projections |

### Benchmark data sources:
- GDC 2025 State of the Industry survey
- Google Cloud gaming AI research (2025)
- Keywords Studios division data (Globalize, Create, Engage)
- Project KARA newsletters (Issues 003-012) — debris modeling, 3D mesh generation, lighting automation, character creation, facial animation, Agent Swarm
- DORA State of DevOps (CI/CD benchmarks)
- Industry reports (BCG, Newzoo)

## Quick Start

```bash
cd pipeline-auditor
pip install anthropic
export ANTHROPIC_API_KEY=your-key-here

# Interactive — choose from example studios
python agent.py

# Direct
python agent.py pipeline_examples/indie_studio.json

# With JSON report output
python agent.py pipeline_examples/aaa_publisher.json --json-output report.json
```

## Example Studios

| File | Studio | Profile | Key Issues |
|------|--------|---------|------------|
| `indie_studio.json` | Pixel Forge Games | 12-person indie, Unity, Steam-only | No QA automation, Google Sheets loc, manual deployment, no player support tooling |
| `mid_size_studio.json` | Horizon Interactive | 85-person live-service, UE5, multi-platform | 25% QA automation, 12-day loc turnaround, unmoderated voice chat, manual lip-sync |
| `aaa_publisher.json` | Titan Entertainment Group | 450-person AAA, 4 titles, 7 platforms, proprietary engine | 48hr perf test turnaround, 15% loc bug rate, manual facial animation, aging support tools, toxicity press coverage |

### Creating your own pipeline JSON

See any example file for the full schema. Key sections: `team_structure`, `tools`, `qa_process`, `localization`, `asset_creation`, `deployment`, `audio`, `player_support`, `trust_and_safety`, `hourly_rates`. The `notes` fields are important — the agent reads them to understand qualitative pain points beyond the numbers.

## Keywords Studios Products Referenced

| Product | Division | What It Does |
|---------|----------|-------------|
| **Mighty Build & Test** | Globalize | AI-powered test automation — defect identification, regression coverage |
| **KantanAI** | Globalize | Game-specific neural MT — 30M+ words, 35 languages, 2-3x speed vs manual |
| **Helpshift** | Engage | AI player support — 50%+ automation, 150+ languages, intent classification |
| **Project KARA Methodology** | Create (Innovation) | AI-infused art pipelines — 3D gen, lighting automation, Agent Swarm |
| **Community Sift** | Engage | Microsoft AI content moderation (KWS is Value-Added Reseller) |
| **ToxMod** | Engage | Modulate proactive voice chat moderation |
| **Lens** | Engage | AI sentiment analysis platform (Slalom/Snowflake partnership) |

## Project Structure

```
pipeline-auditor/
├── agent.py                  # Agentic loop — Claude API with tool use
├── tools.py                  # Tool definitions, benchmarks, KWS solution catalog
├── report.py                 # Terminal report formatting with KWS branding
├── requirements.txt          # anthropic SDK
├── README.md
└── pipeline_examples/
    ├── indie_studio.json     # Pixel Forge Games (12 people)
    ├── mid_size_studio.json  # Horizon Interactive (85 people)
    └── aaa_publisher.json    # Titan Entertainment Group (450 people)
```

## How Tool Use Works

Claude's tool use follows an agentic request-response loop. The key insight: **Claude decides** which tools to call and in what order based on what it sees in the pipeline data. The same agent produces meaningfully different analyses for an indie studio vs. a AAA publisher — not because of branching `if/else` logic, but because the AI reasons about each situation differently.

```python
# Simplified core loop (see agent.py for full implementation)
while True:
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        system=SYSTEM_PROMPT,  # KWS consultant persona + methodology
        tools=TOOL_DEFINITIONS,
        messages=messages,
    )

    for block in response.content:
        if block.type == "tool_use":
            result = execute_tool(block.name, block.input)
            # Send result back to Claude for reasoning...

    if response.stop_reason == "end_turn":
        break  # Agent completed its analysis
```

This is the same agentic pattern explored in Project KARA's Agent Swarm research — specialized AI instances coordinating to complete complex, multi-step tasks.
