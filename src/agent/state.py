"""State schema for the research agent graph."""

from typing import TypedDict, Annotated, List
from operator import add


class Source(TypedDict):
    """A cited source with URL and title."""
    url: str
    title: str
    snippet: str


class ResearchState(TypedDict):
    """State maintained throughout the research graph execution."""
    query: str
    sub_queries: List[str]
    current_sub_query: str
    findings: Annotated[List[str], add]
    sources: Annotated[List[Source], add]
    iteration: int
    max_iterations: int
    report: str
    status: str
    error: str
