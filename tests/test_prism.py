"""
Unit tests for PRISM research assistant.
Tests routing, data structures, and graceful fallback behavior.
"""

import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from tools.router import heuristic_route
from tools.gemini_client import synthesize_research, is_gemini_available
from tools.weather_tool import WMO_WEATHER_CODES
from components.history import generate_markdown_export


def test_weather_routing():
    """Test router accurately identifies weather queries."""
    res = heuristic_route("What is the weather in Tokyo?")
    assert "weather" in res["tools"]
    assert res["weather_city"] is not None
    assert "tokyo" in res["weather_city"].lower()


def test_arxiv_routing():
    """Test router identifies academic and paper queries."""
    res = heuristic_route("Find arXiv research papers on quantum error correction")
    assert "arxiv" in res["tools"]
    assert "quantum" in res["arxiv_query"].lower()


def test_wikipedia_routing():
    """Test router identifies encyclopedic questions."""
    res = heuristic_route("Who was Alan Turing and what was his contribution?")
    assert "wikipedia" in res["tools"]


def test_multi_source_routing():
    """Test router defaults to multi-source synthesis for broad topics."""
    res = heuristic_route("CRISPR Cas9 gene editing technology")
    assert "wikipedia" in res["tools"]
    assert "arxiv" in res["tools"]


def test_wmo_weather_codes():
    """Test weather dictionary codes."""
    assert 0 in WMO_WEATHER_CODES
    desc, emoji = WMO_WEATHER_CODES[0]
    assert "Clear" in desc
    assert emoji in ["☀️", "🌤️"]


def test_synthesis_fallback_without_api_key():
    """Test research synthesis produces clean markdown even without Gemini API key."""
    fake_arxiv = {
        "status": "success",
        "papers": [{
            "title": "Attention Is All You Need",
            "authors_str": "Vaswani et al.",
            "published": "2017-06-12",
            "short_summary": "Introduces Transformer model.",
            "pdf_url": "https://arxiv.org/pdf/1706.03762"
        }]
    }
    fake_wiki = {
        "status": "success",
        "articles": [{
            "title": "Transformer (machine learning)",
            "url": "https://en.wikipedia.org/wiki/Transformer",
            "summary": "A deep learning architecture based on self-attention."
        }]
    }

    report = synthesize_research(
        query="Transformer architecture",
        wiki_data=fake_wiki,
        arxiv_data=fake_arxiv,
        weather_data=None,
        api_key=None
    )

    assert "Research Briefing" in report
    assert "Attention Is All You Need" in report
    assert "Transformer (machine learning)" in report


def test_dossier_export():
    """Test markdown export generation."""
    sample_history = [{
        "timestamp": "2026-11-21 12:00:00",
        "query": "Quantum Computing",
        "tools": ["arxiv", "wikipedia"],
        "reasoning": "Academic literature search",
        "report": "Quantum computing is a rapidly advancing field..."
    }]
    md = generate_markdown_export(sample_history)
    assert "PRISM Research Dossier" in md
    assert "Quantum Computing" in md


if __name__ == "__main__":
    print("Running PRISM tests...")
    test_weather_routing()
    print("[PASS] Weather routing test")
    test_arxiv_routing()
    print("[PASS] arXiv routing test")
    test_wikipedia_routing()
    print("[PASS] Wikipedia routing test")
    test_multi_source_routing()
    print("[PASS] Multi-source routing test")
    test_wmo_weather_codes()
    print("[PASS] WMO codes test")
    test_synthesis_fallback_without_api_key()
    print("[PASS] Synthesis fallback test")
    test_dossier_export()
    print("[PASS] Dossier export test")
    print("\nAll unit tests passed successfully!")
