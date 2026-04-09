"""
Tool definitions and implementations for the pipeline audit agent.

Each tool is a Python function that the agent can call via Claude's tool use.
The TOOL_DEFINITIONS list provides the JSON schema Claude needs to invoke them.

Benchmark data and Keywords Studios solution mappings are informed by:
- Keywords Studios company overview (April 2026)
- Project KARA newsletters (Issues 003-012)
- GDC 2025 State of the Industry / Google Cloud gaming AI research
- Industry benchmarks (BCG, Newzoo, GDC surveys)
"""

import json

# ---------------------------------------------------------------------------
# Industry benchmark data (informed by real industry surveys + KWS data)
# ---------------------------------------------------------------------------
BENCHMARKS = {
    "qa": {
        "category": "Quality Assurance",
        "industry_avg_hours_per_build": 120,
        "top_quartile_hours_per_build": 60,
        "automation_adoption_pct": 68,
        "ai_assisted_bug_detection_pct": 42,
        "avg_bug_escape_rate_pct": 8,
        "top_quartile_bug_escape_rate_pct": 3,
        "kws_benchmark": {
            "mighty_build_test_defect_reduction_pct": 40,
            "kws_in_house_testers": 2400,
            "kws_automation_coverage_pct": 85,
        },
        "source": "GDC 2025 State of the Industry, Keywords Studios QA division data",
    },
    "localization": {
        "category": "Localization",
        "industry_avg_turnaround_days": 14,
        "top_quartile_turnaround_days": 5,
        "ai_translation_adoption_pct": 55,
        "avg_languages_supported": 12,
        "avg_cost_per_word_usd": 0.12,
        "ai_assisted_cost_per_word_usd": 0.04,
        "kws_benchmark": {
            "kantanai_words_translated": "30M+",
            "kantanai_languages": 35,
            "kantanai_speed_multiplier": "2-3x vs manual",
            "kantanai_projects_per_week": 3000,
            "kws_lqa_specialists": 700,
            "kws_languages_supported": "50+",
        },
        "source": "Keywords Studios Globalize division, KantanAI platform data",
    },
    "asset_creation": {
        "category": "Asset Creation",
        "industry_avg_assets_per_artist_per_week": 8,
        "top_quartile_assets_per_artist_per_week": 15,
        "ai_texture_generation_adoption_pct": 35,
        "ai_concept_art_adoption_pct": 28,
        "ai_3d_mesh_generation_adoption_pct": 18,
        "avg_revision_cycles": 4,
        "top_quartile_revision_cycles": 2,
        "kws_benchmark": {
            "project_kara_debris_time_reduction": "8hrs to 2hrs (75%)",
            "project_kara_3d_mesh_gen_time": "under 5 minutes",
            "project_kara_optimization_time": "15 minutes",
            "project_kara_lighting_config_reduction_pct": 78,
            "tools_evaluated_by_kws": "500+",
        },
        "source": "Project KARA newsletters (Issues 004, 009, 010), GDC 2025 presentation",
    },
    "deployment": {
        "category": "Deployment & CI/CD",
        "industry_avg_build_time_minutes": 90,
        "top_quartile_build_time_minutes": 25,
        "avg_deploys_per_week": 3,
        "top_quartile_deploys_per_week": 12,
        "rollback_rate_pct": 15,
        "top_quartile_rollback_rate_pct": 4,
        "source": "Industry CI/CD benchmarks, DORA State of DevOps",
    },
    "audio": {
        "category": "Audio & Voice Production",
        "industry_avg_lines_per_day": 200,
        "top_quartile_lines_per_day": 500,
        "ai_voice_synthesis_adoption_pct": 22,
        "ai_lipsync_adoption_pct": 15,
        "avg_recording_session_hours": 6,
        "post_processing_hours_per_hour_recorded": 3,
        "kws_benchmark": {
            "audio2face_setup_time": "minutes vs days for manual rigging",
            "kws_voiceover_languages": "50+",
            "kws_audio_studios": ["Blindlight (casting)", "Liquid Violet (production)", "Laced (post)"],
            "interactive_media_agreement_2025": "consent + pay parity for AI voice",
        },
        "source": "Project KARA Issue 012, Keywords Studios audio division, Interactive Media Agreement (July 2025)",
    },
    "player_support": {
        "category": "Player Support & Community",
        "industry_avg_first_response_hours": 24,
        "top_quartile_first_response_hours": 4,
        "ai_automation_rate_pct": 30,
        "avg_csat_score": 3.5,
        "top_quartile_csat_score": 4.2,
        "kws_benchmark": {
            "helpshift_automation_rate_pct": 50,
            "helpshift_languages": "150+",
            "helpshift_features": ["AI intent classification", "bot workflows", "Language AI translation"],
            "lens_platform": "AI sentiment analysis (Slalom/Snowflake partnership)",
        },
        "source": "Keywords Studios Engage division, Helpshift platform data",
    },
    "project_management": {
        "category": "Project Management",
        "industry_avg_schedule_overrun_pct": 35,
        "top_quartile_schedule_overrun_pct": 10,
        "ai_planning_adoption_pct": 18,
        "avg_meeting_hours_per_dev_per_week": 12,
        "top_quartile_meeting_hours_per_dev_per_week": 6,
        "source": "GDC 2025 developer survey, industry PM benchmarks",
    },
    "trust_and_safety": {
        "category": "Trust & Safety / Content Moderation",
        "industry_avg_moderation_response_minutes": 30,
        "top_quartile_moderation_response_minutes": 5,
        "ai_moderation_adoption_pct": 45,
        "avg_false_positive_rate_pct": 12,
        "top_quartile_false_positive_rate_pct": 4,
        "kws_benchmark": {
            "community_sift": "Microsoft AI content moderation (Keywords is VAR)",
            "toxmod": "Modulate proactive voice chat moderation",
            "gaming_safety_coalition": "Co-founded with Modulate, ActiveFence, Take This",
        },
        "source": "Keywords Studios Engage division, Gaming Safety Coalition",
    },
}

# ---------------------------------------------------------------------------
# Keywords Studios solution catalog
# ---------------------------------------------------------------------------
KWS_SOLUTIONS = {
    "qa": {
        "primary_product": "Mighty Build & Test",
        "description": (
            "AI-powered game development and testing automation platform. "
            "Automatically tests and identifies defects, allowing issues to be "
            "resolved faster and reducing manual QA workload."
        ),
        "division": "Globalize",
        "engagement_model": "Managed service or platform license",
        "kws_differentiator": "2,400+ in-house testers, all platforms and peripherals",
        "ai_capabilities": [
            "Automated defect identification",
            "Regression test automation",
            "Smoke test coverage",
            "Performance testing on device farm",
        ],
    },
    "localization": {
        "primary_product": "KantanAI",
        "description": (
            "Purpose-built machine translation engines for games that outperform "
            "general-purpose MT models. Cloud-based, available 24/7. Translates "
            "30M+ words across 35 languages with 2-3x speed of manual translation."
        ),
        "division": "Globalize",
        "engagement_model": "Platform + human review (MTPE)",
        "kws_differentiator": "700+ LQA specialists, 50+ languages, gaming-specific MT models",
        "ai_capabilities": [
            "Gaming-specific neural MT engines",
            "Contextual translation with game terminology",
            "Integration with Helpshift for multilingual support",
            "Cultural adaptation and sensitivity review",
        ],
    },
    "asset_creation": {
        "primary_product": "Project KARA Methodology (Innovation-as-a-Service)",
        "description": (
            "AI-infused art pipeline methodology developed through applied R&D. "
            "Covers 3D asset generation, character creation (via Didimo Popul8), "
            "2.5D blockout modeling, automated lighting, and procedural workflows. "
            "Reduces debris modeling from 8hrs to 2hrs, lighting setup by 78%%."
        ),
        "division": "Create",
        "engagement_model": "AI Consultancy (Innovation-as-a-Service)",
        "kws_differentiator": "500+ AI tools evaluated, real production R&D (not theoretical)",
        "ai_capabilities": [
            "AI-assisted 3D mesh generation (Tripo, 3DAI Studio)",
            "GAI concept art generation (Midjourney + style control)",
            "2.5D blockout modeling (MLOPs + Houdini)",
            "Automated lighting pipeline (ChatGPT + Unity)",
            "AI character generation (Didimo Popul8)",
            "Facial animation and lip-sync (Nvidia Audio2Face)",
            "Agent Swarm for scene population and code generation",
        ],
    },
    "audio": {
        "primary_product": "AI-Assisted Audio Pipeline",
        "description": (
            "End-to-end audio services including AI-powered facial animation "
            "(Nvidia Audio2Face), voice casting (Blindlight), production "
            "(Liquid Violet), and post-production (Laced). Ethical AI voice "
            "following Interactive Media Agreement standards."
        ),
        "division": "Create",
        "engagement_model": "Managed service with AI augmentation",
        "kws_differentiator": "Ethical AI voice leadership, 50+ language VO capability",
        "ai_capabilities": [
            "Nvidia Audio2Face lip-sync and facial animation",
            "Move AI single-camera motion capture",
            "AI-assisted audio post-processing",
            "Localized voiceover at scale",
        ],
    },
    "player_support": {
        "primary_product": "Helpshift",
        "description": (
            "AI-driven player support platform providing personalized support "
            "journeys. Achieves 50%+ automation for resolution across all devices "
            "in 150+ languages. Features AI intent classification and gaming-specific "
            "bot workflows."
        ),
        "division": "Engage",
        "engagement_model": "Platform license + managed support",
        "kws_differentiator": "Gaming-specific bots, 150+ languages, 50%+ automation",
        "ai_capabilities": [
            "AI-driven intent classification",
            "Automated resolution workflows",
            "Language AI for multilingual support",
            "Predictive player churn modeling (Lens platform)",
        ],
    },
    "trust_and_safety": {
        "primary_product": "Community Sift + ToxMod",
        "description": (
            "Human moderation teams combined with AI tools. Value-Added Reseller "
            "for Microsoft Community Sift. Partnership with Modulate ToxMod for "
            "proactive voice chat moderation."
        ),
        "division": "Engage",
        "engagement_model": "Managed service + technology platform",
        "kws_differentiator": "Co-founder of Gaming Safety Coalition, Microsoft VAR",
        "ai_capabilities": [
            "AI text and image content moderation (Community Sift)",
            "Proactive voice chat moderation (ToxMod)",
            "AI sentiment analysis (Lens platform)",
            "Cultural sensitivity screening",
        ],
    },
    "project_management": {
        "primary_product": "AI Consultancy (Strategic Consulting)",
        "description": (
            "AI-assisted project planning and velocity prediction. Agent Swarm "
            "technology for automated task decomposition, code generation, and "
            "knowledge base consumption."
        ),
        "division": "Create (Innovation)",
        "engagement_model": "AI Consultancy engagement",
        "kws_differentiator": "Agent Swarm R&D, practical AI integration experience",
        "ai_capabilities": [
            "Agent Swarm for task automation",
            "AI-assisted sprint planning and velocity prediction",
            "Automated status reporting and knowledge base indexing",
            "Codebase analysis and error log summarization",
        ],
    },
}

# ---------------------------------------------------------------------------
# Complexity data
# ---------------------------------------------------------------------------
COMPLEXITY_FACTORS = {
    "low": {"score": 1, "label": "Low", "typical_timeline_weeks": "2-4"},
    "medium": {"score": 2, "label": "Medium", "typical_timeline_weeks": "4-8"},
    "high": {"score": 3, "label": "High", "typical_timeline_weeks": "8-16"},
    "very_high": {"score": 4, "label": "Very High", "typical_timeline_weeks": "16-26"},
}

COMPLEXITY_MATRIX = {
    "qa": {
        "default": "medium",
        "manual_only": "high",
        "partial_automation": "low",
        "selenium": "low",
        "appium": "medium",
        "testrail": "low",
        "testcomplete": "low",
    },
    "localization": {
        "default": "medium",
        "manual_only": "high",
        "google_sheets": "high",
        "crowdin": "low",
        "lokalise": "low",
        "memoq": "low",
        "in_house": "medium",
    },
    "asset_creation": {
        "default": "high",
        "substance_painter": "medium",
        "blender": "medium",
        "maya": "medium",
        "houdini": "medium",
        "photoshop": "medium",
        "zbrush": "medium",
        "proprietary": "very_high",
    },
    "deployment": {
        "default": "medium",
        "jenkins": "low",
        "github_actions": "low",
        "gitlab_ci": "low",
        "manual_only": "high",
        "proprietary": "high",
    },
    "audio": {
        "default": "high",
        "wwise": "medium",
        "fmod": "medium",
        "nuendo": "medium",
        "pro_tools": "medium",
        "manual_only": "very_high",
    },
    "player_support": {
        "default": "medium",
        "zendesk": "low",
        "freshdesk": "low",
        "helpshift": "low",
        "manual_only": "high",
        "email_only": "high",
    },
    "trust_and_safety": {
        "default": "medium",
        "manual_only": "high",
        "community_sift": "low",
        "in_house": "medium",
    },
    "project_management": {
        "default": "low",
        "jira": "low",
        "asana": "low",
        "trello": "low",
        "confluence": "low",
        "spreadsheets": "medium",
    },
}


# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------


def lookup_benchmark(category: str) -> dict:
    """Returns industry benchmark data for a given pipeline category."""
    key = category.lower().replace(" ", "_").replace("-", "_")
    if key in BENCHMARKS:
        return {"status": "found", "data": BENCHMARKS[key]}
    available = list(BENCHMARKS.keys())
    return {
        "status": "not_found",
        "error": f"No benchmark data for '{category}'. Available: {available}",
    }


def lookup_kws_solution(category: str) -> dict:
    """Returns Keywords Studios solution data for a given pipeline area."""
    key = category.lower().replace(" ", "_").replace("-", "_")
    if key in KWS_SOLUTIONS:
        return {"status": "found", "solution": KWS_SOLUTIONS[key]}
    available = list(KWS_SOLUTIONS.keys())
    return {
        "status": "not_found",
        "error": f"No KWS solution data for '{category}'. Available: {available}",
    }


def estimate_savings(
    current_hours: float, ai_reduction_pct: float, hourly_rate: float
) -> dict:
    """Calculates financial impact of AI-driven efficiency gains."""
    hours_saved = current_hours * (ai_reduction_pct / 100)
    annual_savings = hours_saved * hourly_rate * 52  # weekly -> annual
    monthly_savings = annual_savings / 12

    # Tiered implementation cost estimate based on scale
    if annual_savings < 50000:
        impl_cost_range = "$15K-$50K"
        impl_cost_mid = 32500
    elif annual_savings < 200000:
        impl_cost_range = "$50K-$150K"
        impl_cost_mid = 100000
    else:
        impl_cost_range = "$150K-$400K"
        impl_cost_mid = 275000

    months_to_roi = max(1, round(impl_cost_mid / max(monthly_savings, 1)))

    return {
        "current_weekly_hours": current_hours,
        "ai_reduction_pct": ai_reduction_pct,
        "hours_saved_per_week": round(hours_saved, 1),
        "hourly_rate_usd": hourly_rate,
        "estimated_monthly_savings_usd": round(monthly_savings, 2),
        "estimated_annual_savings_usd": round(annual_savings, 2),
        "implementation_cost_range": impl_cost_range,
        "estimated_months_to_roi": months_to_roi,
    }


def assess_complexity(tool_category: str, current_stack: str) -> dict:
    """Rates implementation difficulty for introducing AI into a pipeline area."""
    cat_key = tool_category.lower().replace(" ", "_").replace("-", "_")
    stack_key = current_stack.lower().replace(" ", "_").replace("-", "_").replace(",", "")

    matrix = COMPLEXITY_MATRIX.get(cat_key, {})
    # Try exact match, then check if any key is contained in the stack string
    complexity_key = matrix.get(stack_key)
    if complexity_key is None:
        for known_stack, rating in matrix.items():
            if known_stack != "default" and known_stack in stack_key:
                complexity_key = rating
                break
    if complexity_key is None:
        complexity_key = matrix.get("default", "medium")

    complexity = COMPLEXITY_FACTORS[complexity_key]

    risks = []
    if complexity["score"] >= 3:
        risks.append("Requires dedicated integration engineering resources")
        risks.append("May disrupt existing workflows during transition period")
    if "proprietary" in stack_key or "manual_only" in stack_key:
        risks.append("Limited existing tooling — higher custom development needed")
    if complexity["score"] <= 2:
        risks.append("Well-established integration path — reference implementations available")

    # Add KWS-specific mitigation
    kws_sol = KWS_SOLUTIONS.get(cat_key, {})
    if kws_sol:
        risks.append(
            f"Keywords Studios offers {kws_sol.get('primary_product', 'relevant solutions')} "
            f"via {kws_sol.get('engagement_model', 'consulting engagement')}"
        )

    return {
        "tool_category": tool_category,
        "current_stack": current_stack,
        "complexity_rating": complexity["label"],
        "complexity_score": complexity["score"],
        "typical_timeline": complexity["typical_timeline_weeks"],
        "risks_and_mitigations": risks,
        "kws_solution": kws_sol.get("primary_product", "AI Consultancy"),
        "kws_division": kws_sol.get("division", "Innovation"),
    }


def generate_recommendation(
    bottleneck: str, benchmark_data: dict, savings: dict
) -> dict:
    """Formats a structured recommendation from analysis data."""
    annual = savings.get("estimated_annual_savings_usd", 0)
    severity = (
        "Critical" if annual > 200000
        else "High" if annual > 75000
        else "Medium"
    )

    return {
        "bottleneck": bottleneck,
        "severity": severity,
        "current_state": benchmark_data,
        "projected_impact": savings,
        "recommendation": (
            f"Address '{bottleneck}' bottleneck through AI-assisted automation. "
            f"Projected annual savings: ${annual:,.0f}. "
            f"Estimated ROI within {savings.get('estimated_months_to_roi', '?')} months."
        ),
    }


# ---------------------------------------------------------------------------
# Maturity model
# ---------------------------------------------------------------------------
MATURITY_LEVELS = {
    1: {"label": "Ad-Hoc", "color_hint": "red",
        "description": "No defined process. Manual, reactive, person-dependent."},
    2: {"label": "Emerging", "color_hint": "red",
        "description": "Basic tooling in place but inconsistent. Significant manual effort."},
    3: {"label": "Defined", "color_hint": "yellow",
        "description": "Structured process with some automation. Meets industry average."},
    4: {"label": "Managed", "color_hint": "green",
        "description": "Data-driven, mostly automated, continuous improvement. Top quartile."},
    5: {"label": "Optimized", "color_hint": "green",
        "description": "AI-augmented, fully integrated, industry-leading. Competitive advantage."},
}


def score_pipeline_maturity(
    category: str,
    automation_pct: float,
    has_ai_tooling: bool,
    meets_industry_avg: bool,
    exceeds_industry_avg: bool,
    process_documented: bool,
    notes: str,
) -> dict:
    """Score a pipeline area on a 1-5 maturity scale with diagnostic reasoning."""
    # Calculate base score from inputs
    score = 1
    factors = []

    if automation_pct >= 60:
        score += 2
        factors.append(f"Strong automation at {automation_pct}%")
    elif automation_pct >= 25:
        score += 1
        factors.append(f"Partial automation at {automation_pct}%")
    else:
        factors.append(f"Minimal automation at {automation_pct}%")

    if has_ai_tooling:
        score += 1
        factors.append("AI tooling already in use")
    else:
        factors.append("No AI tooling in current workflow")

    if exceeds_industry_avg:
        score += 1
        factors.append("Exceeds industry average performance")
    elif meets_industry_avg:
        factors.append("Meets but does not exceed industry average")
    else:
        factors.append("Below industry average performance")

    if process_documented:
        score = max(score, 2)  # documented = at least Emerging
        factors.append("Process is documented/structured")
    else:
        score = min(score, 3)  # undocumented caps at Defined
        factors.append("Process is undocumented or ad-hoc")

    score = max(1, min(5, score))
    maturity = MATURITY_LEVELS[score]

    # Determine gap to next level
    if score < 5:
        next_level = MATURITY_LEVELS[score + 1]
        gap_description = f"To reach '{next_level['label']}': increase automation, adopt AI tooling, formalize processes"
    else:
        gap_description = "Industry-leading maturity. Focus on maintaining competitive advantage."

    return {
        "category": category,
        "maturity_score": score,
        "maturity_label": maturity["label"],
        "maturity_description": maturity["description"],
        "factors": factors,
        "gap_to_next_level": gap_description,
        "notes": notes,
    }


def analyze_cross_cutting_risks(
    studio_name: str,
    studio_size: str,
    team_size: int,
    annual_revenue: int,
    maturity_scores: list,
    bottleneck_count: int,
    total_annual_savings: float,
    key_pain_points: list,
) -> dict:
    """Analyze systemic patterns and strategic risks across the full pipeline."""
    risks = []
    opportunities = []
    themes = []

    # Analyze maturity distribution
    avg_maturity = sum(m.get("maturity_score", 2) for m in maturity_scores) / max(len(maturity_scores), 1)
    lowest = min(maturity_scores, key=lambda m: m.get("maturity_score", 5)) if maturity_scores else {}
    highest = max(maturity_scores, key=lambda m: m.get("maturity_score", 0)) if maturity_scores else {}

    if avg_maturity < 2.5:
        themes.append({
            "theme": "Systemic Manual Process Dependency",
            "insight": (
                f"Average pipeline maturity is {avg_maturity:.1f}/5. The studio relies heavily on "
                f"manual processes across most areas. This creates single points of failure — when key "
                f"people leave, institutional knowledge leaves with them. AI augmentation would provide "
                f"the largest relative improvement here."
            ),
        })
    elif avg_maturity < 3.5:
        themes.append({
            "theme": "Uneven Pipeline Maturity",
            "insight": (
                f"Average maturity is {avg_maturity:.1f}/5, but the gap between strongest "
                f"({highest.get('category', '?')}: {highest.get('maturity_score', '?')}) and weakest "
                f"({lowest.get('category', '?')}: {lowest.get('maturity_score', '?')}) areas is significant. "
                f"Weakest links constrain overall throughput — a fast art pipeline means nothing if QA "
                f"can't keep up."
            ),
        })

    # Revenue risk analysis
    savings_pct = (total_annual_savings / max(annual_revenue, 1)) * 100
    if savings_pct > 10:
        risks.append({
            "risk": "Revenue Efficiency Gap",
            "detail": (
                f"Identified savings of ${total_annual_savings:,.0f} represent {savings_pct:.1f}% of "
                f"annual revenue. This level of inefficiency puts the studio at a competitive disadvantage "
                f"against peers who have already adopted AI tooling."
            ),
        })

    # Live-service risk
    live_service_pain = any("live" in p.lower() or "content drop" in p.lower() or "turnaround" in p.lower()
                           for p in key_pain_points)
    if live_service_pain:
        risks.append({
            "risk": "Live-Service Velocity Risk",
            "detail": (
                "Multiple pipeline areas cite content delivery delays. In live-service games, "
                "slow content cadence directly correlates with player churn. Each day of delay "
                "in localization, QA, or asset delivery represents measurable revenue loss."
            ),
        })

    # Talent risk
    manual_heavy = any("manual" in p.lower() or "single" in p.lower() or "one person" in p.lower()
                       for p in key_pain_points)
    if manual_heavy:
        risks.append({
            "risk": "Key-Person Dependency / Talent Risk",
            "detail": (
                "Manual processes depend on specific individuals. If critical team members leave, "
                "the studio faces knowledge loss and process disruption. AI tooling and process "
                "documentation create institutional resilience."
            ),
        })

    # Quality reputation risk
    quality_pain = any("bug" in p.lower() or "escape" in p.lower() or "toxic" in p.lower()
                       or "complaint" in p.lower() for p in key_pain_points)
    if quality_pain:
        risks.append({
            "risk": "Quality & Reputation Exposure",
            "detail": (
                "Elevated bug escape rates, player complaints, or toxicity issues represent "
                "reputational risk. In the age of social media and Steam reviews, quality failures "
                "have outsized impact on player acquisition and retention."
            ),
        })

    # Scale readiness
    if team_size < 50:
        opportunities.append({
            "opportunity": "AI as a Force Multiplier for Small Teams",
            "detail": (
                f"At {team_size} people, AI tooling doesn't replace headcount — it multiplies the "
                f"output of each team member. A small studio with AI-augmented pipelines can compete "
                f"with studios 3-5x its size on content volume and quality."
            ),
        })
    elif team_size > 200:
        opportunities.append({
            "opportunity": "AI-Driven Coordination at Scale",
            "detail": (
                f"At {team_size} people across multiple projects, coordination overhead is the hidden "
                f"tax. AI tools for automated testing, translation, and content moderation reduce the "
                f"cross-team synchronization burden that grows quadratically with team size."
            ),
        })

    # Industry timing
    opportunities.append({
        "opportunity": "AI Adoption Window",
        "detail": (
            "Per GDC 2025, 90% of game developers are integrating AI and 97% believe generative AI "
            "is reshaping the industry. Studios that adopt now build compounding advantages in "
            "pipeline velocity, cost structure, and talent efficiency. Studios that wait will find "
            "themselves competing against AI-augmented rivals with fundamentally different cost structures."
        ),
    })

    return {
        "studio_name": studio_name,
        "average_maturity": round(avg_maturity, 1),
        "weakest_area": lowest.get("category", "Unknown"),
        "strongest_area": highest.get("category", "Unknown"),
        "cross_cutting_themes": themes,
        "strategic_risks": risks,
        "strategic_opportunities": opportunities,
    }


# ---------------------------------------------------------------------------
# Tool dispatch map
# ---------------------------------------------------------------------------
TOOL_DISPATCH = {
    "lookup_benchmark": lookup_benchmark,
    "lookup_kws_solution": lookup_kws_solution,
    "estimate_savings": estimate_savings,
    "assess_complexity": assess_complexity,
    "generate_recommendation": generate_recommendation,
    "score_pipeline_maturity": score_pipeline_maturity,
    "analyze_cross_cutting_risks": analyze_cross_cutting_risks,
}


def execute_tool(name: str, arguments: dict) -> str:
    """Execute a tool by name with the given arguments. Returns JSON string."""
    func = TOOL_DISPATCH.get(name)
    if func is None:
        return json.dumps({"error": f"Unknown tool: {name}"})
    try:
        result = func(**arguments)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Tool execution failed: {str(e)}"})


# ---------------------------------------------------------------------------
# Claude API tool definitions (JSON schema for tool use)
# ---------------------------------------------------------------------------
TOOL_DEFINITIONS = [
    {
        "name": "lookup_benchmark",
        "description": (
            "Look up industry benchmark data for a specific game production pipeline category. "
            "Returns industry averages, top-quartile performance, AI adoption rates, and "
            "Keywords Studios internal benchmarks where available. "
            "Available categories: qa, localization, asset_creation, deployment, audio, "
            "player_support, project_management, trust_and_safety."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": (
                        "The pipeline category to look up benchmarks for. "
                        "Options: qa, localization, asset_creation, deployment, audio, "
                        "player_support, project_management, trust_and_safety."
                    ),
                }
            },
            "required": ["category"],
        },
    },
    {
        "name": "lookup_kws_solution",
        "description": (
            "Look up the Keywords Studios product or service solution for a given pipeline area. "
            "Returns the recommended KWS product (e.g., Mighty Build & Test, KantanAI, Helpshift, "
            "Project KARA methodology), the relevant division (Create, Globalize, Engage), "
            "engagement model, and specific AI capabilities. "
            "Available categories: qa, localization, asset_creation, audio, player_support, "
            "trust_and_safety, project_management."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": (
                        "The pipeline area to look up KWS solutions for. "
                        "Options: qa, localization, asset_creation, audio, player_support, "
                        "trust_and_safety, project_management."
                    ),
                }
            },
            "required": ["category"],
        },
    },
    {
        "name": "estimate_savings",
        "description": (
            "Calculate the financial impact of introducing AI automation into a pipeline area. "
            "Provide current weekly hours spent, expected AI reduction percentage, and hourly "
            "labor rate. Returns annual savings, implementation cost estimate, and months to ROI."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "current_hours": {
                    "type": "number",
                    "description": "Current weekly hours spent on this activity.",
                },
                "ai_reduction_pct": {
                    "type": "number",
                    "description": "Expected percentage reduction from AI automation (0-100).",
                },
                "hourly_rate": {
                    "type": "number",
                    "description": "Fully-loaded hourly cost of labor in USD.",
                },
            },
            "required": ["current_hours", "ai_reduction_pct", "hourly_rate"],
        },
    },
    {
        "name": "assess_complexity",
        "description": (
            "Assess the implementation complexity of introducing AI tooling into a specific "
            "pipeline area given the studio's current technology stack. Returns complexity "
            "rating, timeline, risks, and the relevant Keywords Studios solution."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "tool_category": {
                    "type": "string",
                    "description": (
                        "The pipeline area (e.g., 'qa', 'localization', 'asset_creation', "
                        "'audio', 'player_support', 'trust_and_safety', 'project_management')."
                    ),
                },
                "current_stack": {
                    "type": "string",
                    "description": (
                        "The studio's current tooling for this area "
                        "(e.g., 'jenkins', 'manual_only', 'crowdin', 'wwise')."
                    ),
                },
            },
            "required": ["tool_category", "current_stack"],
        },
    },
    {
        "name": "generate_recommendation",
        "description": (
            "Generate a structured, prioritized recommendation for a specific pipeline "
            "bottleneck, incorporating benchmark comparison data, projected savings, "
            "and severity classification."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "bottleneck": {
                    "type": "string",
                    "description": "Description of the identified bottleneck.",
                },
                "benchmark_data": {
                    "type": "object",
                    "description": "Benchmark comparison data from lookup_benchmark.",
                },
                "savings": {
                    "type": "object",
                    "description": "Projected savings data from estimate_savings.",
                },
            },
            "required": ["bottleneck", "benchmark_data", "savings"],
        },
    },
    {
        "name": "score_pipeline_maturity",
        "description": (
            "Score a specific pipeline area on a 1-5 maturity scale. "
            "1=Ad-Hoc (manual, reactive), 2=Emerging (basic tooling), "
            "3=Defined (structured, meets industry avg), 4=Managed (data-driven, top quartile), "
            "5=Optimized (AI-augmented, industry-leading). "
            "Call this for EACH pipeline area to build a maturity scorecard."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "Pipeline area being scored (e.g., 'QA', 'Localization', 'Asset Creation').",
                },
                "automation_pct": {
                    "type": "number",
                    "description": "Current automation percentage in this area (0-100).",
                },
                "has_ai_tooling": {
                    "type": "boolean",
                    "description": "Whether AI-specific tooling is currently used.",
                },
                "meets_industry_avg": {
                    "type": "boolean",
                    "description": "Whether this area meets or approaches industry average performance.",
                },
                "exceeds_industry_avg": {
                    "type": "boolean",
                    "description": "Whether this area exceeds industry average performance.",
                },
                "process_documented": {
                    "type": "boolean",
                    "description": "Whether the process is documented or structured (vs ad-hoc).",
                },
                "notes": {
                    "type": "string",
                    "description": "Brief diagnostic note explaining the score rationale.",
                },
            },
            "required": ["category", "automation_pct", "has_ai_tooling",
                         "meets_industry_avg", "exceeds_industry_avg",
                         "process_documented", "notes"],
        },
    },
    {
        "name": "analyze_cross_cutting_risks",
        "description": (
            "Analyze systemic patterns, strategic risks, and opportunities across "
            "the studio's entire pipeline. Call this AFTER scoring maturity and generating "
            "all recommendations. Provides cross-cutting themes, competitive risk assessment, "
            "and strategic opportunities."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "studio_name": {
                    "type": "string",
                    "description": "Name of the studio.",
                },
                "studio_size": {
                    "type": "string",
                    "description": "Size category (indie, mid-size, AAA).",
                },
                "team_size": {
                    "type": "integer",
                    "description": "Total team headcount.",
                },
                "annual_revenue": {
                    "type": "integer",
                    "description": "Annual revenue in USD.",
                },
                "maturity_scores": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "Array of maturity score objects from score_pipeline_maturity calls.",
                },
                "bottleneck_count": {
                    "type": "integer",
                    "description": "Number of bottlenecks identified.",
                },
                "total_annual_savings": {
                    "type": "number",
                    "description": "Sum of projected annual savings across all recommendations.",
                },
                "key_pain_points": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Key pain points extracted from the pipeline notes fields.",
                },
            },
            "required": ["studio_name", "studio_size", "team_size", "annual_revenue",
                         "maturity_scores", "bottleneck_count", "total_annual_savings",
                         "key_pain_points"],
        },
    },
]
