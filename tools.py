"""
Tool definitions and implementations for the pipeline audit agent.

Each tool is a Python function that the agent can call via Claude's tool use.
The TOOL_DEFINITIONS list provides the JSON schema Claude needs to invoke them.
"""

import json

# ---------------------------------------------------------------------------
# Industry benchmark data (simulated database)
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
    },
    "localization": {
        "category": "Localization",
        "industry_avg_turnaround_days": 14,
        "top_quartile_turnaround_days": 5,
        "ai_translation_adoption_pct": 55,
        "avg_languages_supported": 12,
        "avg_cost_per_word_usd": 0.12,
        "ai_assisted_cost_per_word_usd": 0.04,
    },
    "asset_creation": {
        "category": "Asset Creation",
        "industry_avg_assets_per_artist_per_week": 8,
        "top_quartile_assets_per_artist_per_week": 15,
        "ai_texture_generation_adoption_pct": 35,
        "ai_concept_art_adoption_pct": 28,
        "avg_revision_cycles": 4,
        "top_quartile_revision_cycles": 2,
    },
    "deployment": {
        "category": "Deployment & CI/CD",
        "industry_avg_build_time_minutes": 90,
        "top_quartile_build_time_minutes": 25,
        "avg_deploys_per_week": 3,
        "top_quartile_deploys_per_week": 12,
        "rollback_rate_pct": 15,
        "top_quartile_rollback_rate_pct": 4,
    },
    "audio": {
        "category": "Audio Production",
        "industry_avg_lines_per_day": 200,
        "top_quartile_lines_per_day": 500,
        "ai_voice_synthesis_adoption_pct": 22,
        "avg_recording_session_hours": 6,
        "post_processing_hours_per_hour_recorded": 3,
    },
    "project_management": {
        "category": "Project Management",
        "industry_avg_schedule_overrun_pct": 35,
        "top_quartile_schedule_overrun_pct": 10,
        "ai_planning_adoption_pct": 18,
        "avg_meeting_hours_per_dev_per_week": 12,
        "top_quartile_meeting_hours_per_dev_per_week": 6,
    },
}

COMPLEXITY_FACTORS = {
    "low": {"score": 1, "label": "Low", "typical_timeline_weeks": "2-4"},
    "medium": {"score": 2, "label": "Medium", "typical_timeline_weeks": "4-8"},
    "high": {"score": 3, "label": "High", "typical_timeline_weeks": "8-16"},
    "very_high": {"score": 4, "label": "Very High", "typical_timeline_weeks": "16-26"},
}

# Complexity ratings by tool category + current stack combinations
COMPLEXITY_MATRIX = {
    "qa": {
        "default": "medium",
        "manual_only": "high",
        "partial_automation": "low",
        "selenium": "low",
        "appium": "medium",
    },
    "localization": {
        "default": "medium",
        "manual_only": "high",
        "crowdin": "low",
        "lokalise": "low",
        "in_house": "medium",
    },
    "asset_creation": {
        "default": "high",
        "substance_painter": "medium",
        "blender": "medium",
        "maya": "medium",
        "photoshop": "medium",
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
        "manual_only": "very_high",
    },
    "project_management": {
        "default": "low",
        "jira": "low",
        "asana": "low",
        "trello": "low",
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


def estimate_savings(
    current_hours: float, ai_reduction_pct: float, hourly_rate: float
) -> dict:
    """Calculates financial impact of AI-driven efficiency gains."""
    hours_saved = current_hours * (ai_reduction_pct / 100)
    annual_savings = hours_saved * hourly_rate * 52  # weekly -> annual
    monthly_savings = annual_savings / 12

    return {
        "current_weekly_hours": current_hours,
        "ai_reduction_pct": ai_reduction_pct,
        "hours_saved_per_week": round(hours_saved, 1),
        "hourly_rate_usd": hourly_rate,
        "estimated_monthly_savings_usd": round(monthly_savings, 2),
        "estimated_annual_savings_usd": round(annual_savings, 2),
        "break_even_note": (
            "Typical AI tooling implementation costs $50K-$200K. "
            f"At ${annual_savings:,.0f}/yr savings, ROI is achieved within "
            f"{max(1, round(150000 / max(annual_savings, 1)))} months (mid-range estimate)."
        ),
    }


def assess_complexity(tool_category: str, current_stack: str) -> dict:
    """Rates implementation difficulty for introducing AI into a pipeline area."""
    cat_key = tool_category.lower().replace(" ", "_").replace("-", "_")
    stack_key = current_stack.lower().replace(" ", "_").replace("-", "_")

    matrix = COMPLEXITY_MATRIX.get(cat_key, {})
    complexity_key = matrix.get(stack_key, matrix.get("default", "medium"))
    complexity = COMPLEXITY_FACTORS[complexity_key]

    risks = []
    if complexity["score"] >= 3:
        risks.append("Requires dedicated integration engineering resources")
        risks.append("May disrupt existing workflows during transition")
    if stack_key in ("proprietary", "manual_only"):
        risks.append("Limited existing tooling — higher custom development needed")
    if complexity["score"] <= 2:
        risks.append("Well-trodden path — many reference implementations available")

    return {
        "tool_category": tool_category,
        "current_stack": current_stack,
        "complexity_rating": complexity["label"],
        "complexity_score": complexity["score"],
        "typical_timeline": complexity["typical_timeline_weeks"],
        "risks": risks,
    }


def generate_recommendation(
    bottleneck: str, benchmark_data: dict, savings: dict
) -> dict:
    """Formats a structured recommendation from analysis data."""
    severity = "Critical" if savings.get("estimated_annual_savings_usd", 0) > 200000 else (
        "High" if savings.get("estimated_annual_savings_usd", 0) > 100000 else "Medium"
    )

    return {
        "bottleneck": bottleneck,
        "severity": severity,
        "current_state": benchmark_data,
        "projected_impact": savings,
        "recommendation": (
            f"Address '{bottleneck}' bottleneck by implementing AI-assisted automation. "
            f"Projected annual savings: ${savings.get('estimated_annual_savings_usd', 0):,.0f}."
        ),
    }


# ---------------------------------------------------------------------------
# Tool dispatch map (name -> function)
# ---------------------------------------------------------------------------
TOOL_DISPATCH = {
    "lookup_benchmark": lookup_benchmark,
    "estimate_savings": estimate_savings,
    "assess_complexity": assess_complexity,
    "generate_recommendation": generate_recommendation,
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
            "Available categories: qa, localization, asset_creation, deployment, audio, project_management."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "The pipeline category to look up benchmarks for (e.g., 'qa', 'localization', 'asset_creation').",
                }
            },
            "required": ["category"],
        },
    },
    {
        "name": "estimate_savings",
        "description": (
            "Calculate the financial impact of introducing AI automation into a pipeline area. "
            "Provide current weekly hours spent, expected AI reduction percentage, and hourly labor rate."
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
            "pipeline area given the studio's current technology stack."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "tool_category": {
                    "type": "string",
                    "description": "The pipeline area (e.g., 'qa', 'localization', 'asset_creation').",
                },
                "current_stack": {
                    "type": "string",
                    "description": "The studio's current tooling for this area (e.g., 'jenkins', 'manual_only', 'crowdin').",
                },
            },
            "required": ["tool_category", "current_stack"],
        },
    },
    {
        "name": "generate_recommendation",
        "description": (
            "Generate a structured recommendation for a specific bottleneck, incorporating "
            "benchmark comparison data and projected savings."
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
]
