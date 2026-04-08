"""
Report formatting for the pipeline audit agent.

Takes the agent's collected recommendations and renders a structured
terminal report with color and layout.
"""

import json
from datetime import datetime
from typing import Optional


# ANSI color codes for terminal output
class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"


def severity_color(severity: str) -> str:
    return {
        "Critical": Colors.RED,
        "High": Colors.YELLOW,
        "Medium": Colors.CYAN,
    }.get(severity, Colors.RESET)


def complexity_color(rating: str) -> str:
    return {
        "Low": Colors.GREEN,
        "Medium": Colors.YELLOW,
        "High": Colors.RED,
        "Very High": Colors.RED + Colors.BOLD,
    }.get(rating, Colors.RESET)


def format_usd(amount: float) -> str:
    return f"${amount:,.0f}"


def print_header(studio_name: str) -> None:
    width = 72
    print()
    print(f"{Colors.BOLD}{'=' * width}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'PIPELINE AUDIT REPORT':^{width}}{Colors.RESET}")
    print(f"{Colors.BOLD}{studio_name:^{width}}{Colors.RESET}")
    print(f"{Colors.DIM}{datetime.now().strftime('%B %d, %Y'):^{width}}{Colors.RESET}")
    print(f"{Colors.BOLD}{'=' * width}{Colors.RESET}")
    print()


def print_executive_summary(recommendations: list) -> None:
    total_savings = sum(
        r.get("projected_impact", {}).get("estimated_annual_savings_usd", 0)
        for r in recommendations
    )
    critical = sum(1 for r in recommendations if r.get("severity") == "Critical")
    high = sum(1 for r in recommendations if r.get("severity") == "High")
    medium = sum(1 for r in recommendations if r.get("severity") == "Medium")

    print(f"{Colors.BOLD}EXECUTIVE SUMMARY{Colors.RESET}")
    print(f"{'─' * 72}")
    print(f"  Total recommendations: {len(recommendations)}")
    print(f"  Severity breakdown:    {Colors.RED}{critical} Critical{Colors.RESET}  |  "
          f"{Colors.YELLOW}{high} High{Colors.RESET}  |  {Colors.CYAN}{medium} Medium{Colors.RESET}")
    print(f"  Total projected annual savings: {Colors.GREEN}{Colors.BOLD}{format_usd(total_savings)}{Colors.RESET}")
    print()


def print_recommendation(idx: int, rec: dict, complexity: Optional[dict] = None) -> None:
    sev = rec.get("severity", "Medium")
    scolor = severity_color(sev)

    print(f"{Colors.BOLD}┌── Recommendation #{idx + 1} ──────────────────────────────────────────┐{Colors.RESET}")
    print(f"│  {Colors.BOLD}Bottleneck:{Colors.RESET}  {rec.get('bottleneck', 'N/A')}")
    print(f"│  {Colors.BOLD}Severity:{Colors.RESET}    {scolor}{sev}{Colors.RESET}")

    impact = rec.get("projected_impact", {})
    if impact:
        print(f"│  {Colors.BOLD}Weekly hours saved:{Colors.RESET}  {impact.get('hours_saved_per_week', 'N/A')}")
        print(f"│  {Colors.BOLD}Annual savings:{Colors.RESET}      {Colors.GREEN}{format_usd(impact.get('estimated_annual_savings_usd', 0))}{Colors.RESET}")

    if complexity:
        crating = complexity.get("complexity_rating", "Unknown")
        ccolor = complexity_color(crating)
        print(f"│  {Colors.BOLD}Implementation:{Colors.RESET}      {ccolor}{crating}{Colors.RESET} "
              f"(~{complexity.get('typical_timeline', '?')} weeks)")
        risks = complexity.get("risks", [])
        if risks:
            print(f"│  {Colors.BOLD}Key risks:{Colors.RESET}")
            for risk in risks:
                print(f"│    • {risk}")

    print(f"│")
    print(f"│  {Colors.DIM}{rec.get('recommendation', '')}{Colors.RESET}")
    print(f"{Colors.BOLD}└{'─' * 71}┘{Colors.RESET}")
    print()


def print_priority_matrix(recommendations: list, complexities: list) -> None:
    print(f"{Colors.BOLD}PRIORITY MATRIX{Colors.RESET}")
    print(f"{'─' * 72}")
    print(f"  {'#':<4} {'Bottleneck':<28} {'Savings':>12} {'Complexity':<12} {'Priority':<10}")
    print(f"  {'─'*4} {'─'*28} {'─'*12} {'─'*12} {'─'*10}")

    items = []
    for i, (rec, comp) in enumerate(zip(recommendations, complexities)):
        savings = rec.get("projected_impact", {}).get("estimated_annual_savings_usd", 0)
        comp_score = comp.get("complexity_score", 2) if comp else 2
        # Priority score: higher savings + lower complexity = higher priority
        priority_score = (savings / 50000) - comp_score
        items.append((i, rec, comp, savings, priority_score))

    items.sort(key=lambda x: x[4], reverse=True)

    for rank, (i, rec, comp, savings, _) in enumerate(items):
        bottleneck = rec.get("bottleneck", "N/A")[:28]
        comp_rating = comp.get("complexity_rating", "?") if comp else "?"
        ccolor = complexity_color(comp_rating)
        priority = ["P0 — Do Now", "P1 — Next", "P2 — Plan", "P3 — Backlog"][min(rank, 3)]
        pcolor = [Colors.RED, Colors.YELLOW, Colors.CYAN, Colors.DIM][min(rank, 3)]

        print(f"  {rank + 1:<4} {bottleneck:<28} {Colors.GREEN}{format_usd(savings):>12}{Colors.RESET} "
              f"{ccolor}{comp_rating:<12}{Colors.RESET} {pcolor}{priority}{Colors.RESET}")

    print()


def print_footer() -> None:
    print(f"{'─' * 72}")
    print(f"{Colors.DIM}  Generated by Pipeline Audit Agent — powered by Claude with tool use{Colors.RESET}")
    print(f"{Colors.DIM}  This report is a simulated demonstration of agentic AI workflows.{Colors.RESET}")
    print(f"{'─' * 72}")
    print()


def render_report(
    studio_name: str,
    recommendations: list,
    complexities: list,
) -> None:
    """Render the full audit report to the terminal."""
    print_header(studio_name)
    print_executive_summary(recommendations)

    for i, rec in enumerate(recommendations):
        comp = complexities[i] if i < len(complexities) else None
        print_recommendation(i, rec, comp)

    if recommendations and complexities:
        print_priority_matrix(recommendations, complexities)

    print_footer()


def save_report_json(
    studio_name: str,
    recommendations: list,
    complexities: list,
    output_path: str,
) -> None:
    """Save the report data as a JSON file."""
    report = {
        "studio_name": studio_name,
        "generated_at": datetime.now().isoformat(),
        "recommendations": recommendations,
        "complexities": complexities,
        "summary": {
            "total_recommendations": len(recommendations),
            "total_annual_savings": sum(
                r.get("projected_impact", {}).get("estimated_annual_savings_usd", 0)
                for r in recommendations
            ),
        },
    }
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n{Colors.GREEN}Report saved to {output_path}{Colors.RESET}")
