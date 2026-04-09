"""
Report formatting for the pipeline audit agent.

Renders a structured terminal report branded for Keywords Studios
AI Consultancy Solutions, with color, layout, KWS solution mappings,
and a priority matrix.
"""

import json
from datetime import datetime
from typing import Optional


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
    width = 76
    print()
    print(f"{Colors.BOLD}{'=' * width}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'KEYWORDS STUDIOS  |  PIPELINE AUDIT REPORT':^{width}}{Colors.RESET}")
    print(f"{Colors.BOLD}{'AI Consultancy Solutions':^{width}}{Colors.RESET}")
    print(f"{Colors.BOLD}{'─' * width}{Colors.RESET}")
    print(f"{Colors.BOLD}{'Client: ' + studio_name:^{width}}{Colors.RESET}")
    print(f"{Colors.DIM}{datetime.now().strftime('%B %d, %Y'):^{width}}{Colors.RESET}")
    print(f"{Colors.BOLD}{'=' * width}{Colors.RESET}")
    print()


def print_executive_summary(recommendations: list, complexities: list) -> None:
    total_savings = sum(
        r.get("projected_impact", {}).get("estimated_annual_savings_usd", 0)
        for r in recommendations
    )
    critical = sum(1 for r in recommendations if r.get("severity") == "Critical")
    high = sum(1 for r in recommendations if r.get("severity") == "High")
    medium = sum(1 for r in recommendations if r.get("severity") == "Medium")

    kws_products = set()
    for c in complexities:
        prod = c.get("kws_solution")
        if prod:
            kws_products.add(prod)

    print(f"{Colors.BOLD}EXECUTIVE SUMMARY{Colors.RESET}")
    print(f"{'─' * 76}")
    print(f"  Recommendations:           {len(recommendations)}")
    print(f"  Severity breakdown:        {Colors.RED}{critical} Critical{Colors.RESET}  |  "
          f"{Colors.YELLOW}{high} High{Colors.RESET}  |  {Colors.CYAN}{medium} Medium{Colors.RESET}")
    print(f"  Projected annual savings:  {Colors.GREEN}{Colors.BOLD}{format_usd(total_savings)}{Colors.RESET}")
    if kws_products:
        print(f"  KWS solutions referenced:  {', '.join(sorted(kws_products))}")
    print()


def print_recommendation(idx: int, rec: dict, complexity: Optional[dict] = None) -> None:
    sev = rec.get("severity", "Medium")
    scolor = severity_color(sev)

    print(f"{Colors.BOLD}+-- Recommendation #{idx + 1} {'─' * 54}+{Colors.RESET}")
    print(f"|  {Colors.BOLD}Bottleneck:{Colors.RESET}   {rec.get('bottleneck', 'N/A')}")
    print(f"|  {Colors.BOLD}Severity:{Colors.RESET}     {scolor}{sev}{Colors.RESET}")

    impact = rec.get("projected_impact", {})
    if impact:
        print(f"|  {Colors.BOLD}Hours saved/wk:{Colors.RESET}  {impact.get('hours_saved_per_week', 'N/A')}")
        print(f"|  {Colors.BOLD}Annual savings:{Colors.RESET}   {Colors.GREEN}{format_usd(impact.get('estimated_annual_savings_usd', 0))}{Colors.RESET}")
        impl_cost = impact.get("implementation_cost_range")
        if impl_cost:
            print(f"|  {Colors.BOLD}Impl. cost:{Colors.RESET}      {impl_cost}")
        roi = impact.get("estimated_months_to_roi")
        if roi:
            print(f"|  {Colors.BOLD}Months to ROI:{Colors.RESET}   {roi}")

    if complexity:
        crating = complexity.get("complexity_rating", "Unknown")
        ccolor = complexity_color(crating)
        print(f"|  {Colors.BOLD}Complexity:{Colors.RESET}      {ccolor}{crating}{Colors.RESET} "
              f"(~{complexity.get('typical_timeline', '?')} weeks)")

        kws_sol = complexity.get("kws_solution")
        kws_div = complexity.get("kws_division")
        if kws_sol:
            print(f"|  {Colors.BOLD}KWS Solution:{Colors.RESET}   {Colors.CYAN}{kws_sol}{Colors.RESET}"
                  f"{Colors.DIM} ({kws_div}){Colors.RESET}" if kws_div else "")

        risks = complexity.get("risks_and_mitigations", complexity.get("risks", []))
        if risks:
            print(f"|  {Colors.BOLD}Risks & mitigations:{Colors.RESET}")
            for risk in risks:
                print(f"|    - {risk}")

    print(f"|")
    rec_text = rec.get("recommendation", "")
    # Word-wrap long recommendation text at 70 chars
    words = rec_text.split()
    lines = []
    current = ""
    for word in words:
        if len(current) + len(word) + 1 > 70:
            lines.append(current)
            current = word
        else:
            current = f"{current} {word}" if current else word
    if current:
        lines.append(current)
    for line in lines:
        print(f"|  {Colors.DIM}{line}{Colors.RESET}")
    print(f"{Colors.BOLD}+{'─' * 75}+{Colors.RESET}")
    print()


def print_priority_matrix(recommendations: list, complexities: list) -> None:
    print(f"{Colors.BOLD}PRIORITY MATRIX{Colors.RESET}")
    print(f"{'─' * 76}")
    print(f"  {'#':<3} {'Bottleneck':<26} {'Savings':>11} {'Complexity':<11} {'KWS Solution':<20} {'Priority'}")
    print(f"  {'─'*3} {'─'*26} {'─'*11} {'─'*11} {'─'*20} {'─'*12}")

    items = []
    for i, rec in enumerate(recommendations):
        comp = complexities[i] if i < len(complexities) else {}
        savings = rec.get("projected_impact", {}).get("estimated_annual_savings_usd", 0)
        comp_score = comp.get("complexity_score", 2) if comp else 2
        priority_score = (savings / 50000) - comp_score
        items.append((i, rec, comp, savings, priority_score))

    items.sort(key=lambda x: x[4], reverse=True)

    for rank, (i, rec, comp, savings, _) in enumerate(items):
        bottleneck = rec.get("bottleneck", "N/A")
        if len(bottleneck) > 26:
            bottleneck = bottleneck[:24] + ".."
        comp_rating = comp.get("complexity_rating", "?") if comp else "?"
        ccolor = complexity_color(comp_rating)
        kws_sol = comp.get("kws_solution", "") if comp else ""
        if len(kws_sol) > 20:
            kws_sol = kws_sol[:18] + ".."
        priority_labels = ["P0 - Do Now", "P1 - Next", "P2 - Plan", "P3 - Backlog", "P4 - Monitor"]
        priority_colors = [Colors.RED, Colors.YELLOW, Colors.CYAN, Colors.DIM, Colors.DIM]
        p_idx = min(rank, len(priority_labels) - 1)
        priority = priority_labels[p_idx]
        pcolor = priority_colors[p_idx]

        print(f"  {rank + 1:<3} {bottleneck:<26} {Colors.GREEN}{format_usd(savings):>11}{Colors.RESET} "
              f"{ccolor}{comp_rating:<11}{Colors.RESET} {Colors.CYAN}{kws_sol:<20}{Colors.RESET} "
              f"{pcolor}{priority}{Colors.RESET}")

    print()


def print_next_steps() -> None:
    print(f"{Colors.BOLD}RECOMMENDED NEXT STEPS{Colors.RESET}")
    print(f"{'─' * 76}")
    print(f"  1. {Colors.BOLD}AI Workshop{Colors.RESET} - Half-day pipeline assessment with KWS Innovation team")
    print(f"  2. {Colors.BOLD}Proof of Concept{Colors.RESET} - 4-6 week pilot on the P0 recommendation")
    print(f"  3. {Colors.BOLD}Strategic Roadmap{Colors.RESET} - Full AI integration plan across all priority areas")
    print(f"  4. {Colors.BOLD}Innovation-as-a-Service{Colors.RESET} - Ongoing R&D partnership (Project KARA model)")
    print()
    print(f"  {Colors.DIM}Contact Keywords Studios AI Consultancy:{Colors.RESET}")
    print(f"  {Colors.DIM}keywordsstudios.com/ai-technology/innovation/consultancy{Colors.RESET}")
    print()


def print_footer() -> None:
    print(f"{'─' * 76}")
    print(f"{Colors.DIM}  Keywords Studios  |  Pipeline Audit Agent{Colors.RESET}")
    print(f"{Colors.DIM}  Powered by Claude (Anthropic) with agentic tool use{Colors.RESET}")
    print(f"{Colors.DIM}  Methodology informed by Project KARA and KWS Innovation R&D{Colors.RESET}")
    print(f"{'─' * 76}")
    print()


def render_report(
    studio_name: str,
    recommendations: list,
    complexities: list,
) -> None:
    """Render the full audit report to the terminal."""
    print_header(studio_name)
    print_executive_summary(recommendations, complexities)

    for i, rec in enumerate(recommendations):
        comp = complexities[i] if i < len(complexities) else None
        print_recommendation(i, rec, comp)

    if recommendations and complexities:
        print_priority_matrix(recommendations, complexities)

    print_next_steps()
    print_footer()


def save_report_json(
    studio_name: str,
    recommendations: list,
    complexities: list,
    output_path: str,
) -> None:
    """Save the report data as a JSON file."""
    kws_products = set()
    for c in complexities:
        prod = c.get("kws_solution")
        if prod:
            kws_products.add(prod)

    report = {
        "meta": {
            "report_type": "Keywords Studios Pipeline Audit",
            "generated_at": datetime.now().isoformat(),
            "methodology": "KWS AI Consultancy - Innovation-as-a-Service",
        },
        "studio_name": studio_name,
        "recommendations": recommendations,
        "complexities": complexities,
        "summary": {
            "total_recommendations": len(recommendations),
            "total_annual_savings": sum(
                r.get("projected_impact", {}).get("estimated_annual_savings_usd", 0)
                for r in recommendations
            ),
            "kws_solutions_referenced": sorted(kws_products),
        },
        "next_steps": [
            "AI Workshop - Half-day pipeline assessment with KWS Innovation team",
            "Proof of Concept - 4-6 week pilot on highest-priority recommendation",
            "Strategic Roadmap - Full AI integration plan across all priority areas",
            "Innovation-as-a-Service - Ongoing R&D partnership (Project KARA model)",
        ],
    }
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n{Colors.GREEN}Report saved to {output_path}{Colors.RESET}")
