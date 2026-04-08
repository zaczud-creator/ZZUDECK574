#!/usr/bin/env python3
"""
Pipeline Audit Agent — an agentic AI workflow using Claude with tool use.

This agent analyzes a game studio's production pipeline configuration,
identifies bottlenecks, benchmarks against industry standards, and produces
a prioritized report of AI-driven optimization recommendations.

Usage:
    python agent.py                                    # interactive menu
    python agent.py pipeline_examples/indie_studio.json  # direct file
    python agent.py pipeline.json --json-output report.json  # save JSON report
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
    RESET = "\033[0m"


def banner():
    print(f"""
{Style.BOLD}{Style.CYAN}╔══════════════════════════════════════════════════════════════╗
║              🎮  Pipeline Audit Agent  🎮                   ║
║         Agentic AI for Game Production Analysis             ║
╚══════════════════════════════════════════════════════════════╝{Style.RESET}
""")


def step_header(step_num: int, total: int, title: str):
    print(f"\n{Style.BOLD}{Style.MAGENTA}── Step {step_num}/{total}: {title} {'─' * (45 - len(title))}{Style.RESET}\n")


def agent_thought(text: str):
    """Display the agent's reasoning / chain-of-thought."""
    for line in text.strip().split("\n"):
        print(f"  {Style.DIM}💭 {line}{Style.RESET}")
    print()


def tool_call_display(name: str, args: dict):
    """Show a tool invocation in the terminal."""
    print(f"  {Style.YELLOW}🔧 Calling tool:{Style.RESET} {Style.BOLD}{name}{Style.RESET}")
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
    if len(lines) > 15:
        lines = lines[:12] + [f"  ... ({len(lines) - 12} more lines)"]
    for line in lines:
        print(f"     {Style.DIM}{line}{Style.RESET}")
    print()


def typing_effect(text: str, delay: float = 0.01):
    """Simulate typing for agent output."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
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
        print(f"  {Style.BOLD}{i}.{Style.RESET} {name} ({size}, {team} people)")

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
# Agent loop
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """\
You are a game production pipeline auditor. You analyze studio pipeline configurations \
and identify opportunities for AI-driven optimization.

You have access to tools for looking up industry benchmarks, estimating cost savings, \
assessing implementation complexity, and generating structured recommendations.

IMPORTANT INSTRUCTIONS:
1. First, carefully read the pipeline configuration provided by the user.
2. Identify the top bottlenecks — areas where the studio is underperforming vs. industry benchmarks.
3. For each bottleneck:
   a. Call lookup_benchmark to get industry comparison data
   b. Call estimate_savings to quantify the financial impact
   c. Call assess_complexity to evaluate implementation difficulty
   d. Call generate_recommendation to create a structured recommendation
4. Analyze at least 3 and at most 5 bottleneck areas.
5. After generating all recommendations, provide a final summary with prioritized action items.

Think step by step. Explain your reasoning before each tool call so the user understands \
your analysis process. Be specific — reference actual numbers from the pipeline config \
and compare them to benchmarks.
"""


def run_agent(pipeline: dict, json_output: Optional[str] = None) -> None:
    """Run the agentic loop: send pipeline to Claude, handle tool calls, render report."""
    client = anthropic.Anthropic()
    studio_name = pipeline.get("studio_name", "Unknown Studio")

    banner()
    print(f"{Style.BOLD}Auditing:{Style.RESET} {studio_name}")
    print(f"{Style.BOLD}Team size:{Style.RESET} {pipeline.get('team_size', '?')}")
    print(f"{Style.BOLD}Active projects:{Style.RESET} {pipeline.get('active_projects', '?')}")
    print(f"{Style.DIM}{'─' * 60}{Style.RESET}")

    user_message = (
        f"Please audit the following game studio pipeline configuration and provide "
        f"optimization recommendations.\n\n"
        f"```json\n{json.dumps(pipeline, indent=2)}\n```"
    )

    messages = [{"role": "user", "content": user_message}]

    recommendations = []
    complexities = []
    step = 0
    total_steps = 5

    step_header(1, total_steps, "Reading Pipeline Config")
    print(f"  {Style.GREEN}✓ Loaded pipeline for {studio_name}{Style.RESET}")
    print(f"  {Style.GREEN}✓ Sending to Claude for analysis...{Style.RESET}\n")

    # Agentic loop — keep going until Claude stops calling tools
    while True:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOL_DEFINITIONS,
            messages=messages,
        )

        # Process each content block, execute tools, collect results
        tool_results = []  # (block, result_str) pairs
        for block in response.content:
            if block.type == "text":
                text = block.text.strip()
                if text:
                    # Detect step transitions from content
                    if any(kw in text.lower() for kw in ["benchmark", "industry"]) and step < 2:
                        step = 2
                        step_header(2, total_steps, "Benchmarking Against Industry")
                    elif any(kw in text.lower() for kw in ["saving", "cost", "financial"]) and step < 3:
                        step = 3
                        step_header(3, total_steps, "Estimating Cost Savings")
                    elif any(kw in text.lower() for kw in ["complex", "implement"]) and step < 4:
                        step = 4
                        step_header(4, total_steps, "Assessing Complexity")
                    elif any(kw in text.lower() for kw in ["recommend", "priorit", "action plan", "summary"]) and step < 5:
                        step = 5
                        step_header(5, total_steps, "Generating Action Plan")

                    agent_thought(text)

            elif block.type == "tool_use":
                tool_call_display(block.name, block.input)

                # Execute the tool once, reuse the result
                result = execute_tool(block.name, block.input)
                tool_result_display(result)
                tool_results.append((block, result))

                # Track recommendations and complexities for the report
                result_data = json.loads(result)
                if block.name == "generate_recommendation" and "error" not in result_data:
                    recommendations.append(result_data)
                elif block.name == "assess_complexity" and "error" not in result_data:
                    complexities.append(result_data)

        # If there were tool uses, send results back to Claude
        if tool_results:
            # Add assistant message (serialize content blocks to dicts)
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

            # Add tool results
            messages.append({"role": "user", "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                }
                for block, result in tool_results
            ]})

        # If Claude is done (end_turn or no more tool calls), break
        if response.stop_reason == "end_turn":
            break

    # Render the final report
    print(f"\n{Style.BOLD}{Style.GREEN}Analysis complete. Generating report...{Style.RESET}\n")
    time.sleep(0.5)

    if recommendations:
        render_report(studio_name, recommendations, complexities)
    else:
        print(f"{Style.YELLOW}No structured recommendations were generated.{Style.RESET}")
        print(f"{Style.DIM}The agent's analysis is shown above.{Style.RESET}")

    # Optionally save JSON report
    if json_output and recommendations:
        save_report_json(studio_name, recommendations, complexities, json_output)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Pipeline Audit Agent — AI-powered game production analysis"
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

    # Check for API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print(f"{Style.RED}Error: ANTHROPIC_API_KEY environment variable not set.{Style.RESET}")
        print(f"Set it with: export ANTHROPIC_API_KEY=your-key-here")
        sys.exit(1)

    # Select pipeline
    if args.pipeline_file:
        pipeline_path = args.pipeline_file
    else:
        pipeline_path = select_pipeline()

    pipeline = load_pipeline(pipeline_path)
    run_agent(pipeline, args.json_output)


if __name__ == "__main__":
    main()
