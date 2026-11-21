"""
History and Export Management for PRISM Research Assistant.
"""

import json
from datetime import datetime
from typing import Dict, Any, List
import streamlit as st


def init_session_state():
    """Initialize necessary Streamlit session state keys."""
    if "research_history" not in st.session_state:
        st.session_state["research_history"] = []
    if "current_report" not in st.session_state:
        st.session_state["current_report"] = None
    if "active_tab" not in st.session_state:
        st.session_state["active_tab"] = "🤖 Smart Assistant"


def add_history_entry(
    query: str,
    tools: List[str],
    report: str,
    wiki_data: Dict[str, Any] = None,
    arxiv_data: Dict[str, Any] = None,
    weather_data: Dict[str, Any] = None,
    reasoning: str = ""
):
    """Save a completed research inquiry to the session history."""
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "query": query,
        "tools": tools,
        "reasoning": reasoning,
        "report": report,
        "arxiv_count": len(arxiv_data.get("papers", [])) if arxiv_data else 0,
        "wiki_count": len(wiki_data.get("articles", [])) if wiki_data else 0,
        "has_weather": bool(weather_data and weather_data.get("status") == "success"),
    }
    st.session_state["research_history"].insert(0, entry)
    st.session_state["current_report"] = entry


def generate_markdown_export(history_list: List[Dict[str, Any]]) -> str:
    """Generate a downloadable Markdown file compiling all research inquiries."""
    md = [
        "# 📑 PRISM Research Dossier",
        f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n",
        "---\n"
    ]
    for i, item in enumerate(history_list, 1):
        md.append(f"## {i}. Query: {item['query']}")
        md.append(f"**Date:** {item['timestamp']} | **Tools:** {', '.join(item['tools'])}")
        if item.get("reasoning"):
            md.append(f"**Routing Logic:** {item['reasoning']}\n")
        md.append("### Intelligence Report")
        md.append(item['report'])
        md.append("\n---\n")

    return "\n".join(md)
