"""
Wikipedia Tool for PRISM Research Assistant.
Provides fast encyclopedia lookup, topic summaries, and reference links via Wikipedia API.
"""

from typing import Dict, Any, List
import wikipedia


def search_wikipedia(
    query: str,
    max_results: int = 3,
    sentences: int = 4
) -> Dict[str, Any]:
    """
    Search Wikipedia for background knowledge, definitions, history, and topic summaries.

    Args:
        query: Subject or question to look up.
        max_results: Maximum number of related articles to check.
        sentences: Number of summary sentences to extract per article.

    Returns:
        Structured dictionary containing articles, summaries, URLs, and LLM context.
    """
    cleaned_query = query.strip()
    if not cleaned_query:
        return {"status": "error", "message": "Query string is empty.", "articles": []}

    wikipedia.set_lang("en")
    wikipedia.set_user_agent("prism-research-assistant/1.0 (academic research tool)")

    try:
        search_titles = wikipedia.search(cleaned_query, results=max_results)
        if not search_titles:
            return {
                "status": "not_found",
                "message": f"No Wikipedia articles found matching '{cleaned_query}'.",
                "articles": [],
                "context_text": "No Wikipedia articles found.",
            }

        articles: List[Dict[str, Any]] = []
        for title in search_titles:
            try:
                page = wikipedia.page(title, auto_suggest=False)
                summary_text = wikipedia.summary(title, sentences=sentences, auto_suggest=False)
                
                articles.append({
                    "title": page.title,
                    "url": page.url,
                    "summary": summary_text,
                    "sections": [s for s in page.sections[:6]],
                })
            except wikipedia.exceptions.DisambiguationError as de:
                # If ambiguous, pick the first option
                if de.options:
                    try:
                        first_opt = de.options[0]
                        page = wikipedia.page(first_opt, auto_suggest=False)
                        summary_text = wikipedia.summary(first_opt, sentences=sentences, auto_suggest=False)
                        articles.append({
                            "title": page.title,
                            "url": page.url,
                            "summary": summary_text,
                            "sections": [s for s in page.sections[:6]],
                        })
                    except Exception:
                        pass
            except (wikipedia.exceptions.PageError, Exception):
                continue

        if not articles:
            return {
                "status": "not_found",
                "message": f"Could not retrieve content for '{cleaned_query}'.",
                "articles": [],
                "context_text": "",
            }

        context_parts = []
        for i, a in enumerate(articles, 1):
            sec_str = ", ".join(a['sections']) if a['sections'] else "Overview"
            context_parts.append(
                f"[Wikipedia {i}] {a['title']}\n"
                f"Summary: {a['summary']}\n"
                f"Key Sections: {sec_str}\n"
                f"Source: {a['url']}"
            )
        context_text = "\n\n".join(context_parts)

        return {
            "status": "success",
            "query": cleaned_query,
            "total_articles": len(articles),
            "articles": articles,
            "context_text": context_text,
            "summary": f"Retrieved {len(articles)} relevant Wikipedia article(s) for '{cleaned_query}'."
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Wikipedia query error: {str(e)}",
            "articles": [],
            "context_text": "",
        }
