"""
PRISM – AI-Powered Research Assistant
Python | Streamlit | Gemini AI | arXiv | Wikipedia | Live Weather API
"""

import streamlit as st
from datetime import datetime

# Import internal tools and components
from tools.arxiv_tool import search_arxiv
from tools.wiki_tool import search_wikipedia
from tools.weather_tool import get_weather
from tools.gemini_client import (
    synthesize_research,
    is_gemini_available,
    generate_response,
    get_api_key,
)
from tools.router import route_query
from components.ui import (
    load_custom_css,
    render_hero,
    render_routing_badges,
)
from components.history import (
    init_session_state,
    add_history_entry,
    generate_markdown_export,
)

# Page configuration
st.set_page_config(
    page_title="PRISM – AI-Powered Research Assistant",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load modern custom CSS
load_custom_css()
init_session_state()

# ---------------------------------------------------------
# SIDEBAR CONTROLS
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚡ **PRISM Settings**")
    st.caption("AI-Powered Research & Synthesis Engine")

    # API Key Input
    stored_key = get_api_key()
    api_key_input = st.text_input(
        "Gemini API Key",
        value=stored_key or "",
        type="password",
        help="Get a free Gemini API key from https://aistudio.google.com/app/apikey",
    )

    if api_key_input:
        st.success("🟢 Gemini API Key Active")
    else:
        st.info("🟡 No API Key set. Basic search tools will work; add key for Gemini AI synthesis.")
        st.markdown("[👉 Get a Free Gemini Key](https://aistudio.google.com/app/apikey)")

    st.markdown("---")

    # Model Selection
    selected_model = st.selectbox(
        "Gemini Model",
        options=["gemini-2.5-flash", "gemini-1.5-flash", "gemini-1.5-pro"],
        index=0,
        help="Select the Gemini model variant for routing and synthesis.",
    )

    # Tool Routing Mode
    st.markdown("### 🧭 **Routing Strategy**")
    routing_mode = st.radio(
        "Routing Mode",
        options=["⚡ Automatic (Smart Router)", "🛠️ Manual Tool Override"],
        index=0,
    )

    manual_tools = []
    if routing_mode == "🛠️ Manual Tool Override":
        manual_tools = st.multiselect(
            "Select Active Tools",
            options=["arxiv", "wikipedia", "weather"],
            default=["arxiv", "wikipedia"],
        )

    st.markdown("---")

    # Sample Presets
    st.markdown("### 💡 **Quick Research Presets**")
    presets = [
        "Quantum Computing fault tolerance breakthroughs",
        "CRISPR-Cas9 gene therapy recent advancements",
        "Transformer attention mechanisms vs SSMs",
        "History and architecture of the Eiffel Tower",
        "Current weather in Tokyo and London",
    ]
    for p in presets:
        if st.button(f"🔍 {p[:32]}...", key=f"btn_{p[:10]}", use_container_width=True):
            st.session_state["preset_query"] = p

    st.markdown("---")
    if st.button("🗑️ Clear Research History", use_container_width=True):
        st.session_state["research_history"] = []
        st.session_state["current_report"] = None
        st.rerun()

# ---------------------------------------------------------
# HERO SECTION
# ---------------------------------------------------------
render_hero()

# ---------------------------------------------------------
# NAVIGATION TABS
# ---------------------------------------------------------
tab_unified, tab_arxiv, tab_wiki, tab_weather, tab_dossier = st.tabs([
    "🧠 Smart Assistant (Auto-Routing)",
    "📚 arXiv Paper Discovery",
    "🌐 Wikipedia Explorer",
    "⛅ Live Global Weather",
    "📑 Research Dossier & Export",
])

# ---------------------------------------------------------
# TAB 1: SMART ASSISTANT (AUTO-ROUTING CHAT)
# ---------------------------------------------------------
with tab_unified:
    st.markdown("#### 🔍 **Unified Multi-Source Research Query**")
    st.write(
        "Ask any question or research topic. **PRISM** automatically routes your inquiry to "
        "the arXiv academic database, Wikipedia encyclopedia, or real-time Weather API, "
        "then synthesizes the intelligence using **Gemini AI**."
    )

    # Pre-fill query if preset clicked
    default_text = st.session_state.pop("preset_query", "")
    user_query = st.text_input(
        "Enter your research topic or question:",
        value=default_text,
        placeholder="e.g. 'What are the newest arXiv papers on Quantum Computing and what is the foundational theory?'",
        key="unified_query_input",
    )

    col_btn1, col_btn2 = st.columns([1, 4])
    with col_btn1:
        run_research = st.button("🚀 Conduct Research", type="primary", use_container_width=True)

    if run_research and user_query.strip():
        with st.spinner("Analyzing intent and routing tools..."):
            # 1. Routing
            if routing_mode == "⚡ Automatic (Smart Router)":
                route_res = route_query(
                    query=user_query,
                    api_key=api_key_input,
                    model_name=selected_model,
                )
                active_tools = route_res.get("tools", ["wikipedia", "arxiv"])
                reasoning = route_res.get("reasoning", "Multi-source research routing.")
                method = route_res.get("routing_method", "Smart Router")
                arxiv_q = route_res.get("arxiv_query", user_query)
                wiki_q = route_res.get("wiki_query", user_query)
                weather_c = route_res.get("weather_city")
            else:
                active_tools = manual_tools
                reasoning = "Manual tool override requested by user."
                method = "Manual Override"
                arxiv_q = user_query
                wiki_q = user_query
                weather_c = user_query

        # Render routing status
        render_routing_badges(active_tools, reasoning, method)

        # 2. Tool Executions
        wiki_data = None
        arxiv_data = None
        weather_data = None

        col_tools = st.columns(len(active_tools) if active_tools else 1)

        tool_idx = 0
        if "arxiv" in active_tools:
            with st.spinner(f"Querying arXiv API for '{arxiv_q}'..."):
                arxiv_data = search_arxiv(arxiv_q, max_results=4)

        if "wikipedia" in active_tools:
            with st.spinner(f"Querying Wikipedia for '{wiki_q}'..."):
                wiki_data = search_wikipedia(wiki_q, max_results=2)

        if "weather" in active_tools:
            city_target = weather_c or user_query
            with st.spinner(f"Fetching live weather for '{city_target}'..."):
                weather_data = get_weather(city_target)

        # 3. Gemini Synthesis
        with st.spinner("Synthesizing multi-source findings with Gemini AI..."):
            synthesis_report = synthesize_research(
                query=user_query,
                wiki_data=wiki_data,
                arxiv_data=arxiv_data,
                weather_data=weather_data,
                api_key=api_key_input,
                model_name=selected_model,
            )

        # Save to history
        add_history_entry(
            query=user_query,
            tools=active_tools,
            report=synthesis_report,
            wiki_data=wiki_data,
            arxiv_data=arxiv_data,
            weather_data=weather_data,
            reasoning=reasoning,
        )

        # 4. Display Results
        st.markdown("### 📋 **AI Research Synthesis**")
        st.markdown(synthesis_report)

        st.markdown("---")
        st.markdown("#### 🔬 **Inspected Multi-Source Raw Data**")

        # Multi-tab raw data views
        sub_tabs = []
        if arxiv_data:
            sub_tabs.append("📚 arXiv Papers")
        if wiki_data:
            sub_tabs.append("🌐 Wikipedia Articles")
        if weather_data:
            sub_tabs.append("⛅ Live Weather Data")

        if sub_tabs:
            created_tabs = st.tabs(sub_tabs)
            tab_map_idx = 0

            if arxiv_data:
                with created_tabs[tab_map_idx]:
                    if arxiv_data.get("papers"):
                        for p in arxiv_data["papers"]:
                            st.markdown(
                                f"""
                                <div class="paper-card">
                                    <div class="paper-title"><a href="{p['pdf_url']}" target="_blank" style="text-decoration:none; color:#818CF8;">📄 {p['title']}</a></div>
                                    <div class="paper-meta"><strong>Authors:</strong> {p['authors_str']} | <strong>Published:</strong> {p['published']} | <strong>Category:</strong> {p['category']}</div>
                                    <div class="paper-abstract">{p['summary']}</div>
                                    <a href="{p['pdf_url']}" target="_blank" style="display:inline-block; padding:4px 10px; background:#4F46E5; color:white; border-radius:6px; text-decoration:none; font-size:0.8rem; font-weight:600;">📥 Open PDF on arXiv</a>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
                    else:
                        st.info(arxiv_data.get("message", "No papers retrieved."))
                tab_map_idx += 1

            if wiki_data:
                with created_tabs[tab_map_idx]:
                    if wiki_data.get("articles"):
                        for a in wiki_data["articles"]:
                            st.markdown(f"#### [{a['title']}]({a['url']})")
                            st.write(a["summary"])
                            if a.get("sections"):
                                st.caption("Key Sections: " + ", ".join(a["sections"]))
                            st.markdown("---")
                    else:
                        st.info(wiki_data.get("message", "No Wikipedia articles retrieved."))
                tab_map_idx += 1

            if weather_data:
                with created_tabs[tab_map_idx]:
                    if weather_data.get("status") == "success":
                        col_w1, col_w2, col_w3, col_w4 = st.columns(4)
                        col_w1.metric("Location", weather_data.get("location"))
                        col_w2.metric("Temperature", f"{weather_data.get('temp_c')} °C", f"{weather_data.get('feels_like_c')} °C feels like")
                        col_w3.metric("Condition", f"{weather_data.get('condition')} {weather_data.get('emoji')}")
                        col_w4.metric("Humidity & Wind", f"{weather_data.get('humidity')}%", f"{weather_data.get('wind_kmh')} km/h")

                        # Daily forecast
                        if weather_data.get("daily_forecast"):
                            st.write("**5-Day Forecast:**")
                            fcols = st.columns(len(weather_data["daily_forecast"]))
                            for i, f in enumerate(weather_data["daily_forecast"]):
                                with fcols[i]:
                                    st.markdown(f"**{f['date']}**")
                                    st.markdown(f"### {f['emoji']}")
                                    st.caption(f"{f['condition']}")
                                    st.write(f"🌡️ {f['max_c']}° / {f['min_c']}°")
                    else:
                        st.warning(weather_data.get("message", "Weather data unavailable."))

# ---------------------------------------------------------
# TAB 2: DEDICATED ARXIV PAPER DISCOVERY
# ---------------------------------------------------------
with tab_arxiv:
    st.markdown("### 📚 **arXiv Academic Paper Explorer**")
    st.write("Search the global repository of 2+ million scientific and academic preprints across Computer Science, Physics, Mathematics, Biology, and Quantitative Finance.")

    col_ax1, col_ax2, col_ax3 = st.columns([3, 1, 1])
    with col_ax1:
        arxiv_input = st.text_input("Enter academic topic or keywords:", "Transformers self-attention optimization", key="arxiv_search_bar")
    with col_ax2:
        arxiv_sort = st.selectbox("Sort By", ["relevance", "submittedDate", "lastUpdatedDate"], index=0)
    with col_ax3:
        arxiv_limit = st.slider("Max Papers", min_value=1, max_value=15, value=5)

    if st.button("🔍 Search arXiv Papers", key="btn_arxiv_search"):
        with st.spinner("Retrieving arXiv preprints..."):
            papers_res = search_arxiv(arxiv_input, max_results=arxiv_limit, sort_by=arxiv_sort)

        if papers_res.get("status") == "success" and papers_res.get("papers"):
            st.success(f"Retrieved {len(papers_res['papers'])} research papers for '{arxiv_input}'")
            for p in papers_res["papers"]:
                st.markdown(
                    f"""
                    <div class="paper-card">
                        <div class="paper-title">📄 {p['title']}</div>
                        <div class="paper-meta">
                            <strong>Authors:</strong> {p['authors_str']} | 
                            <strong>Published:</strong> {p['published']} | 
                            <strong>Category:</strong> <span style="color:#38BDF8;">{p['category']}</span>
                        </div>
                        <div class="paper-abstract">{p['summary']}</div>
                        <a href="{p['pdf_url']}" target="_blank" style="display:inline-block; padding:5px 12px; background:#4F46E5; color:white; border-radius:6px; text-decoration:none; font-size:0.85rem; font-weight:600;">📥 Direct PDF Link</a>
                        <a href="{p['entry_id']}" target="_blank" style="display:inline-block; margin-left:8px; padding:5px 12px; background:#1E293B; color:#94A3B8; border:1px solid #334155; border-radius:6px; text-decoration:none; font-size:0.85rem;">🔗 arXiv Page</a>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.warning(papers_res.get("message", "No papers found."))

# ---------------------------------------------------------
# TAB 3: DEDICATED WIKIPEDIA EXPLORER
# ---------------------------------------------------------
with tab_wiki:
    st.markdown("### 🌐 **Wikipedia Knowledge Explorer**")
    st.write("Extract verified encyclopedic knowledge, historical context, key definitions, and source citations.")

    col_w1, col_w2, col_w3 = st.columns([3, 1, 1])
    with col_w1:
        wiki_input = st.text_input("Enter topic or entity to explore:", "Artificial General Intelligence", key="wiki_search_bar")
    with col_w2:
        wiki_limit = st.slider("Articles", min_value=1, max_value=5, value=2)
    with col_w3:
        wiki_sentences = st.slider("Summary Length (sentences)", min_value=2, max_value=10, value=5)

    if st.button("🌐 Search Wikipedia", key="btn_wiki_search"):
        with st.spinner("Fetching encyclopedic articles..."):
            wiki_res = search_wikipedia(wiki_input, max_results=wiki_limit, sentences=wiki_sentences)

        if wiki_res.get("status") == "success" and wiki_res.get("articles"):
            st.success(f"Retrieved {len(wiki_res['articles'])} articles for '{wiki_input}'")
            for a in wiki_res["articles"]:
                with st.expander(f"📖 {a['title']}", expanded=True):
                    st.write(a["summary"])
                    if a.get("sections"):
                        st.caption("📑 Key Sections: " + ", ".join(a["sections"]))
                    st.markdown(f"[🔗 View Full Wikipedia Page]({a['url']})")
        else:
            st.warning(wiki_res.get("message", "No articles found."))

# ---------------------------------------------------------
# TAB 4: DEDICATED LIVE WEATHER STATION
# ---------------------------------------------------------
with tab_weather:
    st.markdown("### ⛅ **Live Global Weather & Geo-Station**")
    st.write("Real-time live atmospheric information and 5-day forecasts worldwide using Open-Meteo & wttr.in API.")

    col_wt1, col_wt2 = st.columns([3, 1])
    with col_wt1:
        weather_city_input = st.text_input("Enter City Name:", "Tokyo", key="weather_city_bar")
    with col_wt2:
        unit_choice = st.radio("Units", ["Metric (°C)", "Imperial (°F)"], horizontal=True)

    if st.button("⛅ Get Live Weather", key="btn_weather_search"):
        with st.spinner(f"Getting atmospheric data for {weather_city_input}..."):
            w_res = get_weather(weather_city_input)

        if w_res.get("status") == "success":
            temp_display = f"{w_res['temp_c']} °C" if "Metric" in unit_choice else f"{w_res['temp_f']} °F"
            feels_display = f"{w_res['feels_like_c']} °C" if "Metric" in unit_choice else f"{w_res['feels_like_f']} °F"

            st.markdown(
                f"""
                <div class="weather-widget">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <div class="weather-city">📍 {w_res['location']}</div>
                            <div class="weather-condition">{w_res['emoji']} {w_res['condition']}</div>
                        </div>
                        <div class="weather-temp">{temp_display}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            col_met1, col_met2, col_met3, col_met4 = st.columns(4)
            col_met1.metric("Feels Like", feels_display)
            col_met2.metric("Humidity", f"{w_res['humidity']}%")
            col_met3.metric("Wind Speed", f"{w_res['wind_kmh']} km/h")
            col_met4.metric("Source", w_res.get("source", "Open-Meteo"))

            if w_res.get("daily_forecast"):
                st.markdown("#### 📅 5-Day Outlook")
                fcols = st.columns(len(w_res["daily_forecast"]))
                for i, day in enumerate(w_res["daily_forecast"]):
                    with fcols[i]:
                        st.markdown(f"**{day['date']}**")
                        st.markdown(f"## {day['emoji']}")
                        st.caption(day["condition"])
                        st.write(f"High: {day['max_c']}°C\nLow: {day['min_c']}°C")
        else:
            st.error(w_res.get("message", "Unable to retrieve weather."))

# ---------------------------------------------------------
# TAB 5: RESEARCH DOSSIER & EXPORT
# ---------------------------------------------------------
with tab_dossier:
    st.markdown("### 📑 **Research History & Dossier Export**")
    st.write("All research inquiries conducted during this session are archived here. You can download a structured research dossier as a Markdown report.")

    history = st.session_state.get("research_history", [])
    if history:
        col_exp1, col_exp2 = st.columns([2, 1])
        with col_exp1:
            st.info(f"Total Research Briefings Archived: **{len(history)}**")
        with col_exp2:
            export_content = generate_markdown_export(history)
            st.download_button(
                label="📥 Export Dossier (Markdown)",
                data=export_content,
                file_name=f"prism_research_dossier_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown",
                use_container_width=True,
            )

        st.markdown("---")
        for i, item in enumerate(history, 1):
            with st.expander(f"📌 {i}. {item['query']} — ({item['timestamp']})", expanded=(i == 1)):
                st.markdown(f"**Active Tools:** `{', '.join(item['tools'])}` | **Strategy:** {item.get('reasoning', '')}")
                st.markdown("---")
                st.markdown(item["report"])
    else:
        st.write("No research inquiries yet. Conduct research in the **Smart Assistant** tab to build your dossier!")

# Footer
st.markdown("---")
st.caption("⚡ **PRISM** — AI-Powered Research Assistant | Built with Python, Streamlit, Gemini AI, arXiv, Wikipedia & Open-Meteo.")
