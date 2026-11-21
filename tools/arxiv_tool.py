"""
arXiv Tool for PRISM Research Assistant.
Discovers and retrieves research papers, preprints, and academic citations via arXiv API.
"""

from typing import Dict, Any, List
import arxiv


def search_arxiv(
    query: str,
    max_results: int = 5,
    sort_by: str = "relevance"
) -> Dict[str, Any]:
    """
    Search arXiv for research papers matching a query.

    Args:
        query: Subject, keywords, or author to search for.
        max_results: Number of papers to retrieve (default: 5).
        sort_by: "relevance" or "lastUpdatedDate" or "submittedDate".

    Returns:
        Structured dictionary containing paper metadata, summaries, and links.
    """
    cleaned_query = query.strip()
    if not cleaned_query:
        return {"status": "error", "message": "Search query is empty.", "papers": []}

    sort_criterion = arxiv.SortCriterion.Relevance
    if sort_by == "lastUpdatedDate":
        sort_criterion = arxiv.SortCriterion.LastUpdatedDate
    elif sort_by == "submittedDate":
        sort_criterion = arxiv.SortCriterion.SubmittedDate

    try:
        client = arxiv.Client(
            page_size=max_results,
            delay_seconds=1.0,
            num_retries=3
        )
        search = arxiv.Search(
            query=cleaned_query,
            max_results=max_results,
            sort_by=sort_criterion
        )

        papers: List[Dict[str, Any]] = []
        for result in client.results(search):
            authors = [a.name for a in result.authors] if result.authors else ["Unknown"]
            pub_date = result.published.strftime("%Y-%m-%d") if result.published else "N/A"
            primary_cat = result.primary_category if hasattr(result, "primary_category") else "General"
            
            # Clean abstract whitespace
            clean_summary = " ".join(result.summary.split()) if result.summary else "No summary available."

            papers.append({
                "title": result.title.replace("\n", " ").strip(),
                "authors": authors,
                "authors_str": ", ".join(authors[:4]) + (" et al." if len(authors) > 4 else ""),
                "published": pub_date,
                "summary": clean_summary,
                "short_summary": clean_summary[:300] + "..." if len(clean_summary) > 300 else clean_summary,
                "pdf_url": result.pdf_url if hasattr(result, "pdf_url") else "",
                "entry_id": result.entry_id,
                "category": primary_cat,
                "doi": result.doi if hasattr(result, "doi") else None,
            })

        if not papers:
            return {
                "status": "not_found",
                "message": f"No arXiv research papers found for query: '{cleaned_query}'.",
                "papers": [],
                "context_text": "No papers found.",
            }

        # Build context text for Gemini
        context_parts = []
        for i, p in enumerate(papers, 1):
            context_parts.append(
                f"[{i}] {p['title']}\n"
                f"Authors: {p['authors_str']} | Published: {p['published']} | Category: {p['category']}\n"
                f"Abstract: {p['summary']}\n"
                f"PDF: {p['pdf_url']}"
            )
        context_text = "\n\n".join(context_parts)

        return {
            "status": "success",
            "query": cleaned_query,
            "total_found": len(papers),
            "papers": papers,
            "context_text": context_text,
            "summary": f"Discovered {len(papers)} peer-reviewed/preprint research papers on arXiv for '{cleaned_query}'."
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to search arXiv: {str(e)}",
            "papers": [],
            "context_text": "",
        }
