#!/usr/bin/env python3
"""
Pipeline Audit Agent — Keywords Studios AI Consultancy Demo

An agentic AI workflow using Claude with tool use that analyzes game studio
production pipelines, benchmarks against industry standards and Keywords Studios
capabilities, and produces a prioritized report of AI-driven optimization
recommendations with specific KWS product/service mappings.

Demonstrates the kind of analysis Keywords Studios' AI Consultancy Solutions
team performs during client engagements, powered by the same agentic AI
patterns explored in Project KARA.

Usage:
    python agent.py                                       # interactive menu
    python agent.py pipeline_examples/indie_studio.json   # direct file
    python agent.py pipeline.json --json-output report.json
"""

import argparse
import json
import os
import sys
import time
from typing import Optional

import anthropic

from tools import TOOL_DEFINITIONS, execute_tool
from report import render_report, save_report_json


# ---------------------------------------------------------------------------
# Terminal UI helpers
# ---------------------------------------------------------------------------

class Style:
    BOLD = "\033[1m"
    DIM = "\033[2m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    MAGENTA = "\033[95m"
    BLUE = "\033[94m"
    RESET = "\033[0m"


def banner():
    print(f"""
{Style.BOLD}{Style.CYAN}╔══════════════════════════════════════════════════════════════════╗
║         Pipeline Audit Agent  |  Keywords Studios               ║
║         AI Consultancy Solutions  -  Agentic Workflow Demo       ║
╚══════════════════════════════════════════════════════════════════╝{Style.RESET}
{Style.DIM}  Powered by Claude (Anthropic) with tool use
  Methodology informed by Project KARA and KWS Innovation R&D{Style.RESET}
""")


def step_header(step_num: int, total: int, title: str):
    pad = max(0, 50 - len(title))
    print(f"\n{Style.BOLD}{Style.MAGENTA}── Step {step_num}/{total}: {title} {'─' * pad}{Style.RESET}\n")


def agent_thought(text: str):
    """Display the agent's reasoning / chain-of-thought."""
    for line in text.strip().split("\n"):
        print(f"  {Style.DIM}  {line}{Style.RESET}")
    print()


def tool_call_display(name: str, args: dict):
    """Show a tool invocation in the terminal."""
    print(f"  {Style.YELLOW}>> tool call:{Style.RESET} {Style.BOLD}{name}{Style.RESET}")
    for k, v in args.items():
        display_val = json.dumps(v) if isinstance(v, (dict, list)) else str(v)
        if len(display_val) > 80:
            display_val = display_val[:77] + "..."
        print(f"     {Style.DIM}{k}: {display_val}{Style.RESET}")
    print()


def tool_result_display(result_str: str):
    """Show a tool result in the terminal."""
    try:
        data = json.loads(result_str)
        formatted = json.dumps(data, indent=2)
    except json.JSONDecodeError:
        formatted = result_str
    lines = formatted.split("\n")
    if len(lines) > 18:
        lines = lines[:15] + [f"  ... ({len(lines) - 15} more lines)"]
    for line in lines:
        print(f"     {Style.DIM}{line}{Style.RESET}")
    print()


# ---------------------------------------------------------------------------
# Pipeline file loading
# ---------------------------------------------------------------------------

def load_pipeline(path: str) -> dict:
    """Load and validate a pipeline JSON file."""
    if not os.path.exists(path):
        print(f"{Style.RED}Error: File not found: {path}{Style.RESET}")
        sys.exit(1)
    with open(path) as f:
        data = json.load(f)
    required = ["studio_name", "team_structure", "tools"]
    missing = [k for k in required if k not in data]
    if missing:
        print(f"{Style.RED}Error: Pipeline file missing required fields: {missing}{Style.RESET}")
        sys.exit(1)
    return data


def select_pipeline() -> str:
    """Interactive menu to select a pipeline example."""
    examples_dir = os.path.join(os.path.dirname(__file__), "pipeline_examples")
    files = sorted(f for f in os.listdir(examples_dir) if f.endswith(".json"))

    if not files:
        print(f"{Style.RED}No pipeline examples found in {examples_dir}{Style.RESET}")
        sys.exit(1)

    print(f"{Style.BOLD}Available pipeline configurations:{Style.RESET}\n")
    for i, f in enumerate(files, 1):
        path = os.path.join(examples_dir, f)
        with open(path) as fh:
            data = json.load(fh)
        name = data.get("studio_name", f)
        size = data.get("studio_size", "unknown")
        team = data.get("team_size", "?")
        genre = data.get("primary_genre", "")
        extra = f", {genre}" if genre else ""
        print(f"  {Style.BOLD}{i}.{Style.RESET} {name} ({size}, {team} people{extra})")

    print(f"\n  {Style.BOLD}0.{Style.RESET} Enter a custom file path\n")

    while True:
        choice = input(f"{Style.CYAN}Select a pipeline (1-{len(files)}, or 0): {Style.RESET}").strip()
        if choice == "0":
            custom = input(f"{Style.CYAN}Enter path to pipeline JSON: {Style.RESET}").strip()
            return custom
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(files):
                return os.path.join(examples_dir, files[idx])
        except ValueError:
            pass
        print(f"  {Style.RED}Invalid choice. Try again.{Style.RESET}")


# ---------------------------------------------------------------------------
# System prompt — Keywords Studios context baked in
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """\
You are a senior AI consultant at Keywords Studios, the world's largest technical \
and creative services provider to the global video games industry. You are conducting \
a pipeline audit for a prospective or existing client studio.

ABOUT KEYWORDS STUDIOS:
- 70+ studios across 25+ countries, ~13,000 employees
- Three divisions: Create (game dev, art, audio), Globalize (QA, localization), \
Engage (marketing, player support, trust & safety)
- Serves 24 of the top 25 game publishers (Activision Blizzard, EA, Epic, Microsoft, \
Riot, Tencent, Ubisoft, Take-Two, Supercell, Netflix, etc.)
- Key AI products: Mighty Build & Test (QA automation), KantanAI (game-specific MT, \
30M+ words in 35 languages), Helpshift (player support, 50%+ automation in 150+ languages)
- Project KARA: Applied R&D remastering Detonation Racing with AI-infused pipelines. \
Findings include: debris modeling reduced from 8hrs to 2hrs, 3D mesh generation in under \
5 minutes, lighting configuration tasks reduced by 78%, AI character generation via Didimo, \
Agent Swarm for scene population and code generation, Audio2Face for facial animation.
- AI Consultancy Solutions: Innovation-as-a-Service, AI Strategic Consulting, AI Engineering. \
Led by developers who have applied AI technologies and know real benefits and challenges.
- "Human Plus" philosophy: AI augments human creativity, never replaces it. Strict guardrails \
for IP protection, transparency, and responsible use.

YOUR TOOLS:
- lookup_benchmark: Industry benchmark data + KWS internal benchmarks
- lookup_kws_solution: Keywords Studios product/service recommendations for each area
- estimate_savings: Financial impact and ROI projections
- assess_complexity: Implementation difficulty + relevant KWS solution mapping
- generate_recommendation: Structured recommendation with severity rating

AUDIT METHODOLOGY:
1. Read the pipeline configuration carefully. Note studio size, team composition, \
current tools, and pain points described in the notes fields.
2. Identify the top 3-5 bottlenecks where the studio underperforms vs. industry benchmarks.
3. For EACH bottleneck:
   a. lookup_benchmark — get industry comparison data
   b. lookup_kws_solution — identify the relevant Keywords Studios offering
   c. estimate_savings — quantify the financial impact
   d. assess_complexity — evaluate implementation difficulty
   e. generate_recommendation — create a structured recommendation
4. Provide a final prioritized summary.

IMPORTANT GUIDELINES:
- Be specific. Reference actual numbers from the pipeline config and compare them to benchmarks.
- Explain your reasoning before each tool call — the client should understand your thinking.
- Frame recommendations in terms of the Keywords Studios solution that addresses each bottleneck.
- Consider the studio's size and budget when calibrating recommendations (an indie studio \
needs different solutions than a AAA publisher).
- Reference Project KARA findings where relevant to asset creation, lighting, animation, or \
agent swarm applications.
- Be candid about complexity and risks, not just savings.
"""


# ---------------------------------------------------------------------------
# Agent loop
# ---------------------------------------------------------------------------

def run_agent(pipeline: dict, json_output: Optional[str] = None) -> None:
    """Run the agentic loop: send pipeline to Claude, handle tool calls, render report."""
    client = anthropic.Anthropic()
    studio_name = pipeline.get("studio_name", "Unknown Studio")

    banner()
    print(f"{Style.BOLD}Client:{Style.RESET}          {studio_name}")
    print(f"{Style.BOLD}Studio size:{Style.RESET}     {pipeline.get('studio_size', '?')} ({pipeline.get('team_size', '?')} people)")
    print(f"{Style.BOLD}Active titles:{Style.RESET}   {pipeline.get('active_projects', '?')}")
    revenue = pipeline.get("annual_revenue_usd")
    if revenue:
        print(f"{Style.BOLD}Annual revenue:{Style.RESET}  ${revenue:,}")
    print(f"{Style.DIM}{'─' * 65}{Style.RESET}")

    user_message = (
        f"Please conduct a full pipeline audit for this game studio and provide "
        f"prioritized optimization recommendations, mapping each recommendation to "
        f"the relevant Keywords Studios product or service.\n\n"
        f"```json\n{json.dumps(pipeline, indent=2)}\n```"
    )

    messages = [{"role": "user", "content": user_message}]

    recommendations = []
    complexities = []
    step = 0
    total_steps = 5

    step_header(1, total_steps, "Reading Pipeline Config")
    print(f"  {Style.GREEN}  Loaded pipeline for {studio_name}{Style.RESET}")
    print(f"  {Style.GREEN}  Sending to Claude for analysis...{Style.RESET}\n")

    # Agentic loop
    iteration = 0
    max_iterations = 20  # safety limit
    while iteration < max_iterations:
        iteration += 1
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOL_DEFINITIONS,
            messages=messages,
        )

        # Process each content block, execute tools, collect results
        tool_results = []
        for block in response.content:
            if block.type == "text":
                text = block.text.strip()
                if text:
                    # Detect step transitions
                    lower = text.lower()
                    if any(kw in lower for kw in ["benchmark", "industry", "compare"]) and step < 2:
                        step = 2
                        step_header(2, total_steps, "Benchmarking Against Industry Standards")
                    elif any(kw in lower for kw in ["saving", "cost", "financial", "roi"]) and step < 3:
                        step = 3
                        step_header(3, total_steps, "Estimating Cost Savings & ROI")
                    elif any(kw in lower for kw in ["complex", "implement", "risk"]) and step < 4:
                        step = 4
                        step_header(4, total_steps, "Assessing Complexity & KWS Solutions")
                    elif any(kw in lower for kw in ["recommend", "priorit", "action plan", "summary", "conclusion"]) and step < 5:
                        step = 5
                        step_header(5, total_steps, "Generating Prioritized Action Plan")

                    agent_thought(text)

            elif block.type == "tool_use":
                tool_call_display(block.name, block.input)
                result = execute_tool(block.name, block.input)
                tool_result_display(result)
                tool_results.append((block, result))

                # Track data for report
                result_data = json.loads(result)
                if block.name == "generate_recommendation" and "error" not in result_data:
                    recommendations.append(result_data)
                elif block.name == "assess_complexity" and "error" not in result_data:
                    complexities.append(result_data)

        # Send tool results back to Claude
        if tool_results:
            assistant_content = []
            for block in response.content:
                if block.type == "text":
                    assistant_content.append({"type": "text", "text": block.text})
                elif block.type == "tool_use":
                    assistant_content.append({
                        "type": "tool_use",
                        "id": block.id,
                        "name": block.name,
                        "input": block.input,
                    })
            messages.append({"role": "assistant", "content": assistant_content})
            messages.append({"role": "user", "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": blk.id,
                    "content": res,
                }
                for blk, res in tool_results
            ]})

        if response.stop_reason == "end_turn":
            break

    # Render report
    print(f"\n{Style.BOLD}{Style.GREEN}Analysis complete. Generating report...{Style.RESET}\n")
    time.sleep(0.3)

    if recommendations:
        render_report(studio_name, recommendations, complexities)
    else:
        print(f"{Style.YELLOW}No structured recommendations were generated.{Style.RESET}")
        print(f"{Style.DIM}The agent's analysis is shown above.{Style.RESET}")

    if json_output and recommendations:
        save_report_json(studio_name, recommendations, complexities, json_output)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Pipeline Audit Agent — Keywords Studios AI Consultancy Demo"
    )
    parser.add_argument(
        "pipeline_file",
        nargs="?",
        help="Path to pipeline JSON file (interactive menu if omitted)",
    )
    parser.add_argument(
        "--json-output",
        help="Save report as JSON to this path",
    )
    args = parser.parse_args()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print(f"{Style.RED}Error: ANTHROPIC_API_KEY environment variable not set.{Style.RESET}")
        print(f"Set it with: export ANTHROPIC_API_KEY=your-key-here")
        sys.exit(1)

    if args.pipeline_file:
        pipeline_path = args.pipeline_file
    else:
        pipeline_path = select_pipeline()

    pipeline = load_pipeline(pipeline_path)
    run_agent(pipeline, args.json_output)


if __name__ == "__main__":
    main()
