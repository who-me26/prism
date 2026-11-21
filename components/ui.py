"""
UI Components and Styling for PRISM Research Assistant.
"""

import streamlit as st


def load_custom_css():
    """Inject modern styling, custom cards, and badge CSS into Streamlit."""
    st.markdown(
        """
        <style>
        /* Modern font & body layout */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        /* Hero Header */
        .hero-container {
            background: linear-gradient(135deg, rgba(79, 70, 229, 0.15) 0%, rgba(14, 165, 233, 0.15) 100%);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 24px 28px;
            margin-bottom: 24px;
            backdrop-filter: blur(10px);
        }
        .hero-title {
            font-size: 2.2rem;
            font-weight: 800;
            background: linear-gradient(120deg, #818CF8, #38BDF8, #A78BFA);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0;
            letter-spacing: -0.5px;
        }
        .hero-subtitle {
            font-size: 1.05rem;
            color: #94A3B8;
            margin-top: 6px;
            margin-bottom: 0px;
        }

        /* Tool Badges */
        .badge {
            display: inline-flex;
            align-items: center;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.78rem;
            font-weight: 600;
            margin-right: 6px;
            margin-bottom: 6px;
        }
        .badge-arxiv {
            background: rgba(168, 85, 247, 0.18);
            color: #C084FC;
            border: 1px solid rgba(168, 85, 247, 0.4);
        }
        .badge-wiki {
            background: rgba(59, 130, 246, 0.18);
            color: #60A5FA;
            border: 1px solid rgba(59, 130, 246, 0.4);
        }
        .badge-weather {
            background: rgba(16, 185, 129, 0.18);
            color: #34D399;
            border: 1px solid rgba(16, 185, 129, 0.4);
        }
        .badge-router {
            background: rgba(245, 158, 11, 0.18);
            color: #FBBF24;
            border: 1px solid rgba(245, 158, 11, 0.4);
        }

        /* Glass Paper Card */
        .paper-card {
            background: rgba(30, 41, 59, 0.7);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            padding: 16px 20px;
            margin-bottom: 14px;
            transition: all 0.2s ease-in-out;
        }
        .paper-card:hover {
            border-color: rgba(129, 140, 248, 0.4);
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.25);
        }
        .paper-title {
            font-size: 1.08rem;
            font-weight: 700;
            color: #F1F5F9;
            margin-bottom: 4px;
        }
        .paper-meta {
            font-size: 0.82rem;
            color: #94A3B8;
            margin-bottom: 10px;
        }
        .paper-abstract {
            font-size: 0.9rem;
            color: #CBD5E1;
            line-height: 1.55;
            margin-bottom: 12px;
        }

        /* Weather Card */
        .weather-widget {
            background: linear-gradient(135deg, rgba(30, 58, 138, 0.4) 0%, rgba(15, 23, 42, 0.8) 100%);
            border: 1px solid rgba(56, 189, 248, 0.3);
            border-radius: 14px;
            padding: 20px;
            margin-bottom: 16px;
        }
        .weather-temp {
            font-size: 2.8rem;
            font-weight: 800;
            color: #38BDF8;
            line-height: 1;
        }
        .weather-city {
            font-size: 1.3rem;
            font-weight: 700;
            color: #F8FAFC;
        }
        .weather-condition {
            font-size: 1.05rem;
            color: #E2E8F0;
            margin-top: 4px;
        }

        /* Query Chips */
        .sample-query {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 8px 12px;
            font-size: 0.85rem;
            cursor: pointer;
            margin-bottom: 6px;
        }

        /* Routing status banner */
        .routing-banner {
            background: rgba(15, 23, 42, 0.6);
            border-left: 4px solid #6366F1;
            padding: 12px 16px;
            border-radius: 6px;
            margin-bottom: 18px;
            font-size: 0.9rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero():
    """Render the top PRISM header."""
    st.markdown(
        """
        <div class="hero-container">
            <h1 class="hero-title">⚡ PRISM — AI-Powered Research Assistant</h1>
            <p class="hero-subtitle">
                Intelligent multi-source intelligence engine powered by <strong>Gemini AI</strong>. 
                Seamlessly routes between <strong>arXiv</strong> research papers, <strong>Wikipedia</strong> knowledge, and live <strong>Global Weather</strong>.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_routing_badges(tools: list, reasoning: str, method: str):
    """Render visually rich badges showing which tools were triggered."""
    badges_html = ""
    for t in tools:
        if t == "arxiv":
            badges_html += '<span class="badge badge-arxiv">📚 arXiv API</span>'
        elif t == "wikipedia":
            badges_html += '<span class="badge badge-wiki">🌐 Wikipedia</span>'
        elif t == "weather":
            badges_html += '<span class="badge badge-weather">⛅ Live Weather</span>'

    badges_html += f'<span class="badge badge-router">⚡ {method}</span>'

    st.markdown(
        f"""
        <div class="routing-banner">
            <div>{badges_html}</div>
            <div style="margin-top: 6px; color: #CBD5E1; font-size: 0.88rem;">
                <strong>Routing Strategy:</strong> {reasoning}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
