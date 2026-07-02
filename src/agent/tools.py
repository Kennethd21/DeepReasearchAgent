"""Tavily search tool for the research agent."""

import os
from typing import List
from tavily import TavilyClient

from .state import Source


def get_tavily_client() -> TavilyClient:
    """Initialize Tavily client with API key from environment."""
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("TAVILY_API_KEY not found in environment")
    return TavilyClient(api_key=api_key)


def search(query: str, max_results: int = 5) -> List[Source]:
    """Search the web using Tavily and return structured results."""
    client = get_tavily_client()
    
    response = client.search(
        query=query,
        max_results=max_results,
        search_depth="basic",
        include_answer=False
    )
    
    sources: List[Source] = []
    for result in response.get("results", []):
        sources.append(Source(
            url=result.get("url", ""),
            title=result.get("title", "Untitled"),
            snippet=result.get("content", "")
        ))
    
    return sources


def format_sources(sources: List[Source], start_index: int = 1) -> str:
    """Format sources as numbered reference list."""
    lines = []
    for i, source in enumerate(sources, start=start_index):
        lines.append(f"[{i}] {source['title']}\n    {source['url']}\n    {source['snippet'][:200]}...")
    return "\n\n".join(lines)
