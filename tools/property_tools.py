"""
tools/property_tools.py
-----------------------
All tool functions callable by the AutoGen agent.
Each function is self-contained and returns a structured string
so the LLM can reason about results naturally.
"""

from __future__ import annotations
import json
from typing import Literal
import os
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────────────────────────────────────
# Simulated property database (replace with real API / DB in production)
# ─────────────────────────────────────────────────────────────────────────────

PROPERTY_DB: dict = {
    "mumbai": {
        "apartment": [
            {"name": "Sea-View Residency, Worli",        "price_lakh": 250, "bhk": 2, "amenities": ["gym", "pool", "security"], "roi_pct": 6.2},
            {"name": "Bandra West Heights",               "price_lakh": 380, "bhk": 3, "amenities": ["parking", "garden", "clubhouse"], "roi_pct": 5.8},
            {"name": "Navi Mumbai Emerald",               "price_lakh": 95,  "bhk": 1, "amenities": ["security", "lift"],              "roi_pct": 7.1},
        ],
        "villa": [
            {"name": "Juhu Beachfront Villa",             "price_lakh": 950, "bhk": 5, "amenities": ["pool", "garden", "terrace"],     "roi_pct": 4.5},
        ],
        "plot": [
            {"name": "Panvel Residential Plot (500 sqft)","price_lakh": 45,  "bhk": 0, "amenities": [],                               "roi_pct": 9.0},
        ],
    },
    "bangalore": {
        "apartment": [
            {"name": "Whitefield Tech Park Suites",       "price_lakh": 110, "bhk": 2, "amenities": ["gym", "co-working", "pool"],    "roi_pct": 7.8},
            {"name": "Koramangala Urban Nest",            "price_lakh": 180, "bhk": 3, "amenities": ["terrace", "EV charging"],       "roi_pct": 6.9},
            {"name": "Electronic City Starter Home",      "price_lakh": 65,  "bhk": 1, "amenities": ["security", "lift"],             "roi_pct": 8.3},
        ],
        "villa": [
            {"name": "Sarjapur Road Luxury Villa",        "price_lakh": 420, "bhk": 4, "amenities": ["pool", "garden", "smart home"], "roi_pct": 5.5},
        ],
        "plot": [
            {"name": "Devanahalli Growth Plot (1200 sqft)","price_lakh": 60, "bhk": 0, "amenities": [],                               "roi_pct": 11.0},
        ],
    },
    "delhi": {
        "apartment": [
            {"name": "Dwarka Sector-12 Premium",          "price_lakh": 130, "bhk": 3, "amenities": ["gym", "pool", "visitor parking"],"roi_pct": 5.9},
            {"name": "Noida Extension Smart Homes",       "price_lakh": 85,  "bhk": 2, "amenities": ["gym", "security"],              "roi_pct": 7.2},
        ],
        "villa": [
            {"name": "Vasant Kunj Independent House",     "price_lakh": 750, "bhk": 5, "amenities": ["garden", "terrace", "parking"], "roi_pct": 4.2},
        ],
        "plot": [
            {"name": "Greater Noida Residential Plot",    "price_lakh": 55,  "bhk": 0, "amenities": [],                               "roi_pct": 10.5},
        ],
    },
    "hyderabad": {
        "apartment": [
            {"name": "Gachibowli IT Corridor Flats",      "price_lakh": 95,  "bhk": 2, "amenities": ["gym", "pool", "co-working"],    "roi_pct": 8.1},
            {"name": "Jubilee Hills Luxury Apartment",    "price_lakh": 220, "bhk": 3, "amenities": ["concierge", "spa", "pool"],     "roi_pct": 6.4},
        ],
        "villa": [
            {"name": "Narsingi Eco Villa",                "price_lakh": 320, "bhk": 4, "amenities": ["solar", "garden", "rainwater harvesting"], "roi_pct": 5.7},
        ],
        "plot": [
            {"name": "Shamshabad Airport Zone Plot",      "price_lakh": 40,  "bhk": 0, "amenities": [],                               "roi_pct": 12.0},
        ],
    },
}

CITY_PROFILES: dict = {
    "mumbai":    {"avg_price_lakh": 280, "rental_yield_pct": 2.5, "appreciation_5yr_pct": 38, "livability": 7.2, "infra_score": 8.1},
    "bangalore": {"avg_price_lakh": 130, "rental_yield_pct": 3.8, "appreciation_5yr_pct": 52, "livability": 7.8, "infra_score": 7.5},
    "delhi":     {"avg_price_lakh": 160, "rental_yield_pct": 2.8, "appreciation_5yr_pct": 30, "livability": 6.9, "infra_score": 8.3},
    "hyderabad": {"avg_price_lakh": 105, "rental_yield_pct": 4.1, "appreciation_5yr_pct": 61, "livability": 8.2, "infra_score": 7.9},
    "pune":      {"avg_price_lakh": 100, "rental_yield_pct": 3.5, "appreciation_5yr_pct": 44, "livability": 8.0, "infra_score": 7.2},
    "chennai":   {"avg_price_lakh": 90,  "rental_yield_pct": 3.2, "appreciation_5yr_pct": 35, "livability": 7.5, "infra_score": 7.0},
}


# ─────────────────────────────────────────────────────────────────────────────
# Tool 1 — recommend_property
# ─────────────────────────────────────────────────────────────────────────────

def recommend_property(
    location: str,
    budget_lakh: float,
    property_type: Literal["apartment", "villa", "plot"] = "apartment",
) -> str:
    """
    Recommend properties in a given city that fit within budget.

    Args:
        location      : City name (e.g. 'mumbai', 'bangalore')
        budget_lakh   : Maximum budget in Indian Lakhs (₹)
        property_type : 'apartment' | 'villa' | 'plot'

    Returns:
        JSON string with list of matching properties + advisory note.
    """
    city = location.lower().strip()
    ptype = property_type.lower().strip()

    if city not in PROPERTY_DB:
        return json.dumps({
            "status": "error",
            "message": f"City '{city}' not in database. Available: {list(PROPERTY_DB.keys())}",
        })

    listings = PROPERTY_DB[city].get(ptype, [])
    matches = [p for p in listings if p["price_lakh"] <= budget_lakh]

    if not matches:
        return json.dumps({
            "status": "no_match",
            "message": f"No {ptype}s found in {city.title()} within ₹{budget_lakh}L. "
                       f"Consider increasing budget or trying a different type.",
            "suggestions": [p["name"] for p in listings[:2]],
        })

    matches.sort(key=lambda x: x["roi_pct"], reverse=True)
    return json.dumps({
        "status": "success",
        "city": city.title(),
        "property_type": ptype,
        "budget_lakh": budget_lakh,
        "matches": matches,
        "top_pick": matches[0]["name"],
        "advisory": (
            f"Top pick based on ROI: {matches[0]['name']} "
            f"(₹{matches[0]['price_lakh']}L, {matches[0]['roi_pct']}% annual ROI)."
        ),
    }, indent=2)


# ─────────────────────────────────────────────────────────────────────────────
# Tool 2 — compare_locations
# ─────────────────────────────────────────────────────────────────────────────

def compare_locations(location1: str, location2: str) -> str:
    """
    Compare two cities across real-estate metrics.

    Args:
        location1 : First city name
        location2 : Second city name

    Returns:
        JSON string with side-by-side comparison + recommendation.
    """
    c1, c2 = location1.lower().strip(), location2.lower().strip()
    missing = [c for c in [c1, c2] if c not in CITY_PROFILES]
    if missing:
        return json.dumps({
            "status": "error",
            "message": f"Cities not in database: {missing}. Available: {list(CITY_PROFILES.keys())}",
        })

    p1, p2 = CITY_PROFILES[c1], CITY_PROFILES[c2]

    # Simple scoring: weighted sum
    def score(p: dict) -> float:
        return (
            p["rental_yield_pct"] * 2.0 +
            p["appreciation_5yr_pct"] * 0.5 +
            p["livability"] * 1.5 +
            p["infra_score"] * 1.0
        )

    s1, s2 = score(p1), score(p2)
    winner = c1.title() if s1 >= s2 else c2.title()

    return json.dumps({
        "status": "success",
        "comparison": {
            c1.title(): {**p1, "composite_score": round(s1, 2)},
            c2.title(): {**p2, "composite_score": round(s2, 2)},
        },
        "recommendation": winner,
        "reasoning": (
            f"{winner} scores higher overall. "
            f"Key differentiator: "
            f"{'rental yield' if p1['rental_yield_pct'] != p2['rental_yield_pct'] else '5-yr appreciation'}."
        ),
    }, indent=2)


# ─────────────────────────────────────────────────────────────────────────────
# Tool 3 — investment_advice
# ─────────────────────────────────────────────────────────────────────────────

def investment_advice(budget_lakh: float, duration_years: int) -> str:
    """
    Provide strategic investment advice based on budget and time horizon.

    Args:
        budget_lakh    : Available investment budget in Lakhs (₹)
        duration_years : Investment holding period in years

    Returns:
        JSON string with tailored strategy, expected returns, and risk profile.
    """
    strategies = []

    if duration_years <= 2:
        horizon = "short-term"
        if budget_lakh < 50:
            strategies = [
                {"strategy": "REITs (Real Estate Investment Trusts)",
                 "expected_return_pct": 8.5, "risk": "Low",
                 "reason": "Liquid, diversified, no direct ownership needed."},
                {"strategy": "Residential Plot in Tier-2 city",
                 "expected_return_pct": 10.0, "risk": "Medium",
                 "reason": "Lower entry price; good short-term appreciation near highways."},
            ]
        else:
            strategies = [
                {"strategy": "Residential apartment in IT hub",
                 "expected_return_pct": 9.0, "risk": "Medium",
                 "reason": "High rental demand from professionals; quick resale."},
                {"strategy": "Pre-launch unit in upcoming micro-market",
                 "expected_return_pct": 12.0, "risk": "Medium-High",
                 "reason": "Pre-launch prices 15-20% below market; early appreciation."},
            ]
    elif duration_years <= 7:
        horizon = "medium-term"
        strategies = [
            {"strategy": "2BHK in Tier-1 city tech corridor",
             "expected_return_pct": 11.5, "risk": "Medium",
             "reason": "Steady rental + appreciation in established tech hubs."},
            {"strategy": "Commercial space in Grade-A business park",
             "expected_return_pct": 10.5, "risk": "Medium",
             "reason": "Long leases, 6-9% rental yield, stable tenants."},
        ]
    else:
        horizon = "long-term"
        strategies = [
            {"strategy": "Residential land near metro expansion",
             "expected_return_pct": 14.0, "risk": "Medium",
             "reason": "Infrastructure growth catalyses multi-fold appreciation."},
            {"strategy": "Build-to-rent residential unit",
             "expected_return_pct": 13.0, "risk": "Medium-High",
             "reason": "Rental income + capital appreciation over 10+ years."},
            {"strategy": "Diversified portfolio (apartment + REIT)",
             "expected_return_pct": 11.0, "risk": "Low-Medium",
             "reason": "Balance of liquidity (REIT) and physical asset appreciation."},
        ]

    # Simple future value estimate using top strategy
    best = max(strategies, key=lambda s: s["expected_return_pct"])
    fv = budget_lakh * ((1 + best["expected_return_pct"] / 100) ** duration_years)

    return json.dumps({
        "status": "success",
        "budget_lakh": budget_lakh,
        "duration_years": duration_years,
        "horizon": horizon,
        "recommended_strategies": strategies,
        "best_strategy": best["strategy"],
        "projected_value_lakh": round(fv, 2),
        "projected_gain_lakh": round(fv - budget_lakh, 2),
        "disclaimer": (
            "These are indicative projections based on historical averages. "
            "Actual returns may vary. Consult a SEBI-registered advisor for personalized advice."
        ),
    }, indent=2)


# ─────────────────────────────────────────────────────────────────────────────
# Tool 4 — user_profile_memory (in-memory store; session-scoped)
# ─────────────────────────────────────────────────────────────────────────────

_PROFILE_STORE: dict[str, dict] = {}  # session_id -> profile dict


def update_user_profile(
    session_id: str,
    budget_lakh: float | None = None,
    preferred_city: str | None = None,
    property_type: str | None = None,
    purpose: str | None = None,
    additional_notes: str | None = None,
) -> str:
    """
    Store or update the user's real-estate preferences for this session.

    Args:
        session_id       : Unique session identifier
        budget_lakh      : Budget in Lakhs
        preferred_city   : City of interest
        property_type    : apartment | villa | plot
        purpose          : 'self_use' | 'investment' | 'rental'
        additional_notes : Any extra preferences

    Returns:
        JSON string confirming saved profile.
    """
    if session_id not in _PROFILE_STORE:
        _PROFILE_STORE[session_id] = {}

    profile = _PROFILE_STORE[session_id]
    if budget_lakh is not None:
        profile["budget_lakh"] = budget_lakh
    if preferred_city is not None:
        profile["preferred_city"] = preferred_city.lower().strip()
    if property_type is not None:
        profile["property_type"] = property_type.lower().strip()
    if purpose is not None:
        profile["purpose"] = purpose.lower().strip()
    if additional_notes is not None:
        profile.setdefault("notes", []).append(additional_notes)

    return json.dumps({"status": "saved", "profile": profile}, indent=2)

def get_user_profile(session_id: str) -> str:
    """
    Retrieve the stored profile for a session.

    Args:
        session_id : Unique session identifier

    Returns:
        JSON string with user profile or empty profile message.
    """
    profile = _PROFILE_STORE.get(session_id, {})
    if not profile:
        return json.dumps({"status": "empty", "message": "No profile data yet."})
    return json.dumps({"status": "found", "profile": profile}, indent=2)

# ─────────────────────────────────────────────────────────────────────────────
# Tool 5 — web-search 
# ─────────────────────────────────────────────────────────────────────────────

client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def web_search(query: str) -> str:
    print(" WEB SEARCH CALLED:", query)

    try:
        result = client.search(
            query=query,
            search_depth="advanced",
            max_results=5
        )

        if not result.get("results"):
            return "No relevant web results found."

        insights = []
        for r in result["results"]:
            title = r.get("title", "")
            content = r.get("content", "")
            insights.append(f"{title}: {content[:200]}")

        return "\n\n".join(insights)

    except Exception as e:
        return f"Web search error: {str(e)}"

