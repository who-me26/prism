"""
Intelligent Tool Router for PRISM Research Assistant.
Classifies user intent and routes queries to arXiv, Wikipedia, Weather API, or multi-source synthesis.
"""

import re
import json
from typing import Dict, Any, List, Optional
from tools.gemini_client import is_gemini_available, get_client


WEATHER_KEYWORDS = [
    r"\bweather\b", r"\btemperature\b", r"\bforecast\b", r"\brain\b",
    r"\bsnow\b", r"\bhumidity\b", r"\bwind\b", r"\bclimate in\b",
    r"\bdegrees\b", r"\bcelsius\b", r"\bfahrenheit\b", r"\bhow hot\b",
    r"\bhow cold\b", r"\bsunny\b", r"\bcloudy\b", r"\bstorm\b"
]

ARXIV_KEYWORDS = [
    r"\barxiv\b", r"\bpaper\b", r"\bpapers\b", r"\bresearch\b",
    r"\bstudy\b", r"\bstudies\b", r"\bpreprint\b", r"\bjournal\b",
    r"\bliterature\b", r"\balgorithm\b", r"\bstate of the art\b",
    r"\bsota\b", r"\bbenchmarks?\b", r"\bnovel approach\b", r"\bneural\b",
    r"\bquantum\b", r"\bdeep learning\b", r"\bmachine learning\b",
    r"\btransformer\b", r"\bllms?\b", r"\bscientific\b", r"\bphysics\b",
    r"\bastrophysics\b", r"\bmathematics\b", r"\bbiology\b", r"\bgenomics\b",
    r"\bcomputer science\b"
]

WIKI_KEYWORDS = [
    r"\bwho is\b", r"\bwho was\b", r"\bwhat is\b", r"\bwhat are\b",
    r"\bdefine\b", r"\bdefinition\b", r"\bhistory of\b", r"\bbiography\b",
    r"\boverview of\b", r"\bbackground on\b", r"\bwikipedia\b",
    r"\btimeline\b", r"\borigin of\b", r"\bconcept\b", r"\bexplain\b"
]


def _extract_city(query: str) -> Optional[str]:
    """Extract a candidate city from a weather query using regex."""
    patterns = [
        r"(?:weather|forecast|temperature|climate)\s+(?:in|for|at|of)\s+([A-Za-z\s]+?)(?:\?|$|\.|\,)",
        r"(?:in|for)\s+([A-Za-z\s]+?)\s+(?:weather|forecast|temperature)",
        r"how (?:hot|cold) is it in\s+([A-Za-z\s]+?)(?:\?|$)",
    ]
    for p in patterns:
        m = re.search(p, query, re.IGNORECASE)
        if m:
            city = m.group(1).strip()
            # filter out non-city words
            stop_words = {"the", "today", "tomorrow", "this week", "right now", "currently"}
            for sw in stop_words:
                city = re.sub(rf"\b{sw}\b", "", city, flags=re.IGNORECASE).strip()
            if city:
                return city
    return None


def heuristic_route(query: str) -> Dict[str, Any]:
    """
    Fast rule-based heuristic routing when Gemini API is unavailable or for instant classification.
    """
    q_lower = query.lower()

    has_weather = any(re.search(kw, q_lower) for kw in WEATHER_KEYWORDS)
    has_arxiv = any(re.search(kw, q_lower) for kw in ARXIV_KEYWORDS)
    has_wiki = any(re.search(kw, q_lower) for kw in WIKI_KEYWORDS)

    tools = []
    arxiv_q = query
    wiki_q = query
    weather_city = None

    if has_weather:
        weather_city = _extract_city(query)
        if not weather_city:
            # check last words
            parts = query.replace("?", "").split()
            if len(parts) >= 2 and parts[-2].lower() in ["in", "for"]:
                weather_city = parts[-1]
            else:
                weather_city = parts[-1] if parts else "London"
        tools.append("weather")

    if has_arxiv:
        tools.append("arxiv")
        # Clean arxiv query
        arxiv_q = re.sub(r"\b(arxiv|papers?|research|find|search for|latest|show me)\b", "", query, flags=re.IGNORECASE).strip()
        arxiv_q = arxiv_q if arxiv_q else query

    if has_wiki or (not has_arxiv and not has_weather):
        tools.append("wikipedia")
        # Clean wiki query
        wiki_q = re.sub(r"\b(what is|who is|who was|define|tell me about|wikipedia|history of)\b", "", query, flags=re.IGNORECASE).strip()
        wiki_q = wiki_q if wiki_q else query

    # If user asks a broad topic without explicit tool words, query both Wiki and arXiv for comprehensive research!
    if not has_weather and not has_arxiv and not has_wiki:
        tools = ["wikipedia", "arxiv"]
        reasoning = "General research inquiry: synthesizing encyclopedic background (Wikipedia) with academic literature (arXiv)."
    elif len(tools) > 1:
        reasoning = f"Multi-source synthesis query: routing across {', '.join([t.capitalize() for t in tools])}."
    elif "weather" in tools:
        reasoning = f"Live meteorological query: checking current conditions and forecast for {weather_city}."
    elif "arxiv" in tools:
        reasoning = "Academic inquiry: discovering peer-reviewed papers and preprints on arXiv."
    else:
        reasoning = "Encyclopedic inquiry: retrieving structured knowledge and overview from Wikipedia."

    return {
        "tools": tools,
        "arxiv_query": arxiv_q,
        "wiki_query": wiki_q,
        "weather_city": weather_city,
        "reasoning": reasoning,
        "routing_method": "Heuristic Rule Router",
    }


ROUTER_SYSTEM_PROMPT = """You are the Tool Routing Engine of PRISM (AI-Powered Research Assistant).
Analyze the user's research query and decide which tools to invoke:
- "arxiv": for academic papers, preprints, AI/ML, mathematics, physics, theoretical computer science, cutting-edge science.
- "wikipedia": for background knowledge, definitions, history, biographies, established concepts, general facts.
- "weather": for live atmospheric, meteorological, or temperature inquiries for a given location.

You may select multiple tools if the inquiry benefits from multi-source synthesis.

Output strictly valid JSON with this exact structure:
{
  "tools": ["arxiv", "wikipedia", "weather"],
  "arxiv_query": "concise search phrase for arXiv or null",
  "wiki_query": "concise search phrase for Wikipedia or null",
  "weather_city": "City name or null",
  "reasoning": "One concise sentence explaining routing decision"
}
"""


def route_query(
    query: str,
    api_key: Optional[str] = None,
    model_name: str = "gemini-2.5-flash",
    use_ai_router: bool = True
) -> Dict[str, Any]:
    """
    Intelligently route a query using Gemini AI (with heuristic fallback).
    """
    if not use_ai_router or not is_gemini_available(api_key):
        return heuristic_route(query)

    try:
        client = get_client(api_key)
        response = client.models.generate_content(
            model=model_name,
            contents=f"Analyze and route this query:\n'{query}'",
            config={
                "temperature": 0.1,
                "system_instruction": ROUTER_SYSTEM_PROMPT,
                "response_mime_type": "application/json",
            }
        )

        resp_text = response.text.strip()
        data = json.loads(resp_text)

        # Validate tools list
        tools = [t for t in data.get("tools", []) if t in ["arxiv", "wikipedia", "weather"]]
        if not tools:
            return heuristic_route(query)

        return {
            "tools": tools,
            "arxiv_query": data.get("arxiv_query") or query,
            "wiki_query": data.get("wiki_query") or query,
            "weather_city": data.get("weather_city"),
            "reasoning": data.get("reasoning", "Intelligently routed by Gemini AI."),
            "routing_method": "Gemini AI Intelligent Router",
        }
    except Exception:
        # Graceful fallback to heuristic router
        fallback = heuristic_route(query)
        fallback["routing_method"] = "Heuristic Rule Router (AI fallback)"
        return fallback
