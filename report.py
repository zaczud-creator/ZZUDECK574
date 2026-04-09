"""
Report formatting for the pipeline audit agent.

Renders a structured terminal report with:
- Executive Summary
- Pipeline Maturity Scorecard
- Detailed Recommendations with KWS solution mapping
- Cross-Cutting Strategic Analysis
- Executive Narrative (agent's synthesized insight)
- Priority Matrix
- Recommended Next Steps
"""

import json
import textwrap
from datetime import datetime
from typing import Optional


class C:
    """ANSI color codes."""
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    UNDERLINE = "\033[4m"
    RESET = "\033[0m"


W = 78  # report width


def severity_color(severity: str) -> str:
    return {"Critical": C.RED, "High": C.YELLOW, "Medium": C.CYAN}.get(severity, C.RESET)


def complexity_color(rating: str) -> str:
    return {"Low": C.GREEN, "Medium": C.YELLOW, "High": C.RED,
            "Very High": C.RED + C.BOLD}.get(rating, C.RESET)


def maturity_color(score: int) -> str:
    if score <= 2:
        return C.RED
    if score == 3:
        return C.YELLOW
    return C.GREEN


def maturity_bar(score: int) -> str:
    filled = score
    empty = 5 - score
    color = maturity_color(score)
    return f"{color}{'█' * filled}{C.DIM}{'░' * empty}{C.RESET}"


def usd(amount: float) -> str:
    return f"${amount:,.0f}"


def wrap(text: str, indent: str = "|  ", width: int = 72) -> list:
    return textwrap.wrap(text, width=width, initial_indent=indent,
                         subsequent_indent=indent)


# ---------------------------------------------------------------------------
# Report sections
# ---------------------------------------------------------------------------

def print_header(studio_name: str) -> None:
    print()
    print(f"{C.BOLD}{'=' * W}{C.RESET}")
    print(f"{C.BOLD}{C.HEADER}{'KEYWORDS STUDIOS  |  PIPELINE AUDIT REPORT':^{W}}{C.RESET}")
    print(f"{C.BOLD}{'AI Consultancy Solutions':^{W}}{C.RESET}")
    print(f"{C.BOLD}{'─' * W}{C.RESET}")
    print(f"{C.BOLD}{'Client: ' + studio_name:^{W}}{C.RESET}")
    print(f"{C.DIM}{datetime.now().strftime('%B %d, %Y'):^{W}}{C.RESET}")
    print(f"{C.BOLD}{'=' * W}{C.RESET}")
    print()


def print_executive_summary(
    recommendations: list,
    complexities: list,
    maturity_scores: list,
) -> None:
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

    avg_maturity = (sum(m.get("maturity_score", 0) for m in maturity_scores)
                    / max(len(maturity_scores), 1)) if maturity_scores else 0

    print(f"{C.BOLD}EXECUTIVE SUMMARY{C.RESET}")
    print(f"{'─' * W}")
    print(f"  Recommendations:           {len(recommendations)}")
    print(f"  Severity breakdown:        {C.RED}{critical} Critical{C.RESET}  |  "
          f"{C.YELLOW}{high} High{C.RESET}  |  {C.CYAN}{medium} Medium{C.RESET}")
    print(f"  Projected annual savings:  {C.GREEN}{C.BOLD}{usd(total_savings)}{C.RESET}")
    if maturity_scores:
        mc = maturity_color(round(avg_maturity))
        print(f"  Avg pipeline maturity:     {mc}{avg_maturity:.1f}/5.0{C.RESET}")
    if kws_products:
        print(f"  KWS solutions identified:  {', '.join(sorted(kws_products))}")
    print()


def print_maturity_scorecard(maturity_scores: list) -> None:
    if not maturity_scores:
        return

    print(f"{C.BOLD}PIPELINE MATURITY SCORECARD{C.RESET}")
    print(f"{'─' * W}")
    print(f"  {'Area':<22} {'Score':^7} {'Level':<12} {'Bar':^11} {'Diagnostic'}")
    print(f"  {'─'*22} {'─'*7} {'─'*12} {'─'*11} {'─'*20}")

    for m in sorted(maturity_scores, key=lambda x: x.get("maturity_score", 0)):
        cat = m.get("category", "?")
        if len(cat) > 22:
            cat = cat[:20] + ".."
        score = m.get("maturity_score", 0)
        label = m.get("maturity_label", "?")
        mc = maturity_color(score)
        bar = maturity_bar(score)

        # Build a short diagnostic from factors
        factors = m.get("factors", [])
        diag = factors[0] if factors else ""
        if len(diag) > 30:
            diag = diag[:28] + ".."

        print(f"  {cat:<22} {mc}{score:^7}{C.RESET} {mc}{label:<12}{C.RESET} {bar}  {C.DIM}{diag}{C.RESET}")

    # Summary line
    avg = sum(m.get("maturity_score", 0) for m in maturity_scores) / max(len(maturity_scores), 1)
    lowest = min(maturity_scores, key=lambda x: x.get("maturity_score", 5))
    print()
    print(f"  {C.BOLD}Average:{C.RESET} {avg:.1f}/5.0    "
          f"{C.BOLD}Weakest:{C.RESET} {C.RED}{lowest.get('category', '?')}{C.RESET} "
          f"({lowest.get('maturity_score', '?')}/5)")
    print()


def print_recommendation(idx: int, rec: dict, complexity: Optional[dict] = None) -> None:
    sev = rec.get("severity", "Medium")
    scolor = severity_color(sev)

    print(f"{C.BOLD}+-- Recommendation #{idx + 1} {'─' * (W - 24)}+{C.RESET}")
    print(f"|  {C.BOLD}Bottleneck:{C.RESET}   {rec.get('bottleneck', 'N/A')}")
    print(f"|  {C.BOLD}Severity:{C.RESET}     {scolor}{sev}{C.RESET}")

    impact = rec.get("projected_impact", {})
    if impact:
        print(f"|  {C.BOLD}Hours saved/wk:{C.RESET}  {impact.get('hours_saved_per_week', 'N/A')}")
        print(f"|  {C.BOLD}Annual savings:{C.RESET}   {C.GREEN}{usd(impact.get('estimated_annual_savings_usd', 0))}{C.RESET}")
        impl_cost = impact.get("implementation_cost_range")
        if impl_cost:
            print(f"|  {C.BOLD}Impl. cost:{C.RESET}      {impl_cost}")
        roi = impact.get("estimated_months_to_roi")
        if roi:
            print(f"|  {C.BOLD}Months to ROI:{C.RESET}   {roi}")

    if complexity:
        crating = complexity.get("complexity_rating", "Unknown")
        ccolor = complexity_color(crating)
        print(f"|  {C.BOLD}Complexity:{C.RESET}      {ccolor}{crating}{C.RESET} "
              f"(~{complexity.get('typical_timeline', '?')} weeks)")

        kws_sol = complexity.get("kws_solution")
        kws_div = complexity.get("kws_division")
        if kws_sol:
            div_str = f"{C.DIM} ({kws_div}){C.RESET}" if kws_div else ""
            print(f"|  {C.BOLD}KWS Solution:{C.RESET}   {C.CYAN}{kws_sol}{C.RESET}{div_str}")

        risks = complexity.get("risks_and_mitigations", complexity.get("risks", []))
        if risks:
            print(f"|  {C.BOLD}Risks & mitigations:{C.RESET}")
            for risk in risks:
                for line in textwrap.wrap(risk, width=68):
                    print(f"|    - {line}")

    print(f"|")
    rec_text = rec.get("recommendation", "")
    for line in wrap(rec_text, indent="|  ", width=72):
        print(f"{C.DIM}{line}{C.RESET}")
    print(f"{C.BOLD}+{'─' * (W - 1)}+{C.RESET}")
    print()


def print_cross_cutting_analysis(analysis: dict) -> None:
    if not analysis:
        return

    print(f"{C.BOLD}STRATEGIC ANALYSIS{C.RESET}")
    print(f"{'─' * W}")

    themes = analysis.get("cross_cutting_themes", [])
    for theme in themes:
        print(f"\n  {C.BOLD}{C.YELLOW}{theme.get('theme', '')}{C.RESET}")
        for line in textwrap.wrap(theme.get("insight", ""), width=72, initial_indent="  ",
                                  subsequent_indent="  "):
            print(f"  {C.DIM}{line}{C.RESET}")

    risks = analysis.get("strategic_risks", [])
    if risks:
        print(f"\n  {C.BOLD}{C.RED}Strategic Risks{C.RESET}")
        for risk in risks:
            print(f"\n    {C.BOLD}{risk.get('risk', '')}{C.RESET}")
            for line in textwrap.wrap(risk.get("detail", ""), width=68, initial_indent="    ",
                                      subsequent_indent="    "):
                print(f"    {C.DIM}{line}{C.RESET}")

    opps = analysis.get("strategic_opportunities", [])
    if opps:
        print(f"\n  {C.BOLD}{C.GREEN}Strategic Opportunities{C.RESET}")
        for opp in opps:
            print(f"\n    {C.BOLD}{opp.get('opportunity', '')}{C.RESET}")
            for line in textwrap.wrap(opp.get("detail", ""), width=68, initial_indent="    ",
                                      subsequent_indent="    "):
                print(f"    {C.DIM}{line}{C.RESET}")
    print()


def print_narrative(narrative: str) -> None:
    if not narrative:
        return

    print(f"{C.BOLD}EXECUTIVE NARRATIVE{C.RESET}")
    print(f"{'─' * W}")
    # Clean up markdown formatting for terminal
    for paragraph in narrative.split("\n\n"):
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        # Handle markdown headers
        if paragraph.startswith("###"):
            header = paragraph.lstrip("#").strip()
            print(f"\n  {C.BOLD}{C.CYAN}{header}{C.RESET}")
        elif paragraph.startswith("##"):
            header = paragraph.lstrip("#").strip()
            print(f"\n  {C.BOLD}{C.HEADER}{header}{C.RESET}")
        elif paragraph.startswith("#"):
            header = paragraph.lstrip("#").strip()
            print(f"\n  {C.BOLD}{C.UNDERLINE}{header}{C.RESET}")
        elif paragraph.startswith("- ") or paragraph.startswith("* "):
            # Bullet list
            for bullet in paragraph.split("\n"):
                bullet = bullet.strip().lstrip("-*").strip()
                if bullet:
                    for line in textwrap.wrap(bullet, width=70, initial_indent="    - ",
                                              subsequent_indent="      "):
                        print(line)
        else:
            # Regular paragraph — strip inline markdown bold
            clean = paragraph.replace("**", "")
            for line in textwrap.wrap(clean, width=72, initial_indent="  ",
                                      subsequent_indent="  "):
                print(line)
        print()


def print_priority_matrix(recommendations: list, complexities: list) -> None:
    print(f"{C.BOLD}PRIORITY MATRIX{C.RESET}")
    print(f"{'─' * W}")
    print(f"  {'#':<3} {'Bottleneck':<24} {'Savings':>11} {'Cmplx':<7} {'KWS Solution':<22} {'Priority'}")
    print(f"  {'─'*3} {'─'*24} {'─'*11} {'─'*7} {'─'*22} {'─'*12}")

    items = []
    for i, rec in enumerate(recommendations):
        comp = complexities[i] if i < len(complexities) else {}
        savings = rec.get("projected_impact", {}).get("estimated_annual_savings_usd", 0)
        comp_score = comp.get("complexity_score", 2) if comp else 2
        priority_score = (savings / 50000) - comp_score
        items.append((i, rec, comp, savings, priority_score))

    items.sort(key=lambda x: x[4], reverse=True)

    priority_labels = ["P0 - Do Now", "P1 - Next", "P2 - Plan", "P3 - Backlog", "P4 - Monitor"]
    priority_colors = [C.RED, C.YELLOW, C.CYAN, C.DIM, C.DIM]

    for rank, (i, rec, comp, savings, _) in enumerate(items):
        bottleneck = rec.get("bottleneck", "N/A")
        if len(bottleneck) > 24:
            bottleneck = bottleneck[:22] + ".."
        comp_rating = comp.get("complexity_rating", "?") if comp else "?"
        if len(comp_rating) > 7:
            comp_rating = comp_rating[:5] + ".."
        ccolor = complexity_color(comp_rating)
        kws_sol = comp.get("kws_solution", "") if comp else ""
        if len(kws_sol) > 22:
            kws_sol = kws_sol[:20] + ".."
        p_idx = min(rank, len(priority_labels) - 1)

        print(f"  {rank + 1:<3} {bottleneck:<24} {C.GREEN}{usd(savings):>11}{C.RESET} "
              f"{ccolor}{comp_rating:<7}{C.RESET} {C.CYAN}{kws_sol:<22}{C.RESET} "
              f"{priority_colors[p_idx]}{priority_labels[p_idx]}{C.RESET}")
    print()


def print_next_steps() -> None:
    print(f"{C.BOLD}RECOMMENDED ENGAGEMENT PATH{C.RESET}")
    print(f"{'─' * W}")
    steps = [
        ("AI Discovery Workshop", "Half-day session with KWS Innovation team. Map current pipeline, identify quick wins, and align on priorities."),
        ("Proof of Concept", "4-6 week focused pilot on the P0 recommendation. Measurable success criteria defined upfront."),
        ("Strategic Roadmap", "Full AI integration plan across all priority areas. Phased implementation with milestones and KPIs."),
        ("Innovation-as-a-Service", "Ongoing R&D partnership modeled on Project KARA. Continuous evaluation of emerging AI tools and techniques."),
    ]
    for i, (title, desc) in enumerate(steps, 1):
        print(f"  {C.BOLD}{i}. {title}{C.RESET}")
        for line in textwrap.wrap(desc, width=68, initial_indent="     ",
                                  subsequent_indent="     "):
            print(f"{C.DIM}{line}{C.RESET}")
    print()
    print(f"  {C.DIM}Contact: keywordsstudios.com/ai-technology/innovation/consultancy{C.RESET}")
    print()


def print_footer() -> None:
    print(f"{'─' * W}")
    print(f"{C.DIM}  Keywords Studios  |  Pipeline Audit Agent{C.RESET}")
    print(f"{C.DIM}  Powered by Claude (Anthropic) with agentic tool use{C.RESET}")
    print(f"{C.DIM}  Methodology: Project KARA + KWS AI Consultancy Solutions{C.RESET}")
    print(f"{'─' * W}")
    print()


# ---------------------------------------------------------------------------
# Main render
# ---------------------------------------------------------------------------

def render_report(
    studio_name: str,
    recommendations: list,
    complexities: list,
    maturity_scores: Optional[list] = None,
    cross_cutting: Optional[dict] = None,
    narrative: Optional[str] = None,
) -> None:
    """Render the full audit report to the terminal."""
    print_header(studio_name)
    print_executive_summary(recommendations, complexities, maturity_scores or [])

    # Maturity scorecard
    if maturity_scores:
        print_maturity_scorecard(maturity_scores)

    # Narrative analysis (agent's synthesis)
    if narrative:
        print_narrative(narrative)

    # Cross-cutting strategic analysis
    if cross_cutting:
        print_cross_cutting_analysis(cross_cutting)

    # Individual recommendations
    if recommendations:
        print(f"{C.BOLD}DETAILED RECOMMENDATIONS{C.RESET}")
        print(f"{'─' * W}")
        print()
    for i, rec in enumerate(recommendations):
        comp = complexities[i] if i < len(complexities) else None
        print_recommendation(i, rec, comp)

    # Priority matrix
    if recommendations and complexities:
        print_priority_matrix(recommendations, complexities)

    print_next_steps()
    print_footer()


def save_report_json(
    studio_name: str,
    recommendations: list,
    complexities: list,
    output_path: str,
    maturity_scores: Optional[list] = None,
    cross_cutting: Optional[dict] = None,
    narrative: Optional[str] = None,
) -> None:
    """Save the full report data as a JSON file."""
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
        "maturity_assessment": maturity_scores or [],
        "recommendations": recommendations,
        "complexities": complexities,
        "strategic_analysis": cross_cutting,
        "executive_narrative": narrative,
        "summary": {
            "total_recommendations": len(recommendations),
            "total_annual_savings": sum(
                r.get("projected_impact", {}).get("estimated_annual_savings_usd", 0)
                for r in recommendations
            ),
            "average_maturity": (
                round(sum(m.get("maturity_score", 0) for m in maturity_scores)
                      / max(len(maturity_scores), 1), 1)
                if maturity_scores else None
            ),
            "kws_solutions_referenced": sorted(kws_products),
        },
        "next_steps": [
            "AI Discovery Workshop - Half-day pipeline assessment with KWS Innovation team",
            "Proof of Concept - 4-6 week pilot on highest-priority recommendation",
            "Strategic Roadmap - Full AI integration plan across all priority areas",
            "Innovation-as-a-Service - Ongoing R&D partnership (Project KARA model)",
        ],
    }
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n{C.GREEN}Report saved to {output_path}{C.RESET}")
