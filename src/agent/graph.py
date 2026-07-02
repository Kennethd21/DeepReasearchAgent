"""LangGraph StateGraph for the deep research agent."""

import os
from typing import Literal
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END

from .state import ResearchState, Source
from .tools import search, format_sources

load_dotenv()


def get_llm(temperature: float = 0.3) -> ChatGoogleGenerativeAI:
    """Initialize Gemini LLM."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment")
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=api_key,
        temperature=temperature
    )


def decompose_query(state: ResearchState) -> dict:
    """Break complex query into sub-queries for thorough research."""
    llm = get_llm()
    
    prompt = f"""Break this research query into 2-3 specific sub-queries that together would provide comprehensive information.

Original query: {state['query']}

Return ONLY the sub-queries, one per line, prefixed with numbers (1. 2. 3.).
Do not include any explanation."""
    
    response = llm.invoke(prompt)
    lines = response.content.strip().split("\n")
    
    sub_queries = []
    for line in lines:
        line = line.strip()
        if line and line[0].isdigit():
            cleaned = line.lstrip("0123456789. ").strip()
            if cleaned:
                sub_queries.append(cleaned)
    
    if not sub_queries:
        sub_queries = [state['query']]
    
    return {
        "sub_queries": sub_queries,
        "current_sub_query": sub_queries[0],
        "iteration": 0,
        "findings": [],
        "sources": [],
        "status": "decomposed"
    }


def search_node(state: ResearchState) -> dict:
    """Execute search for current sub-query."""
    query = state["current_sub_query"]
    
    try:
        sources = search(query, max_results=3)
        
        findings_text = f"**Search results for:** {query}\n\n"
        for i, source in enumerate(sources, 1):
            findings_text += f"{i}. {source['title']}\n   {source['snippet'][:300]}\n\n"
        
        return {
            "findings": [findings_text],
            "sources": sources,
            "iteration": state["iteration"] + 1,
            "status": "searched"
        }
    except Exception as e:
        return {
            "findings": [f"Search error for '{query}': {str(e)}"],
            "sources": [],
            "iteration": state["iteration"] + 1,
            "status": "search_error"
        }


def evaluate_node(state: ResearchState) -> dict:
    """Evaluate findings and decide if more research is needed."""
    llm = get_llm()
    
    all_findings = "\n".join(state["findings"])
    sources_text = format_sources(state["sources"])
    
    prompt = f"""Based on these research findings, evaluate if we have enough information.

Original query: {state['query']}
Current sub-query: {state['current_sub_query']}
Findings so far: {all_findings[:2000]}

Respond with exactly one word:
- "continue" if we need more research on different sub-queries
- "synthesize" if we have enough to write the report"""
    
    response = llm.invoke(prompt)
    decision = response.content.strip().lower()
    
    return {"status": decision}


def synthesize_node(state: ResearchState) -> dict:
    """Aggregate all findings into a structured markdown report with citations."""
    llm = get_llm()
    
    all_findings = "\n\n".join(state["findings"])
    sources_text = format_sources(state["sources"])
    
    prompt = f"""Create a comprehensive research report based on these findings.

Original query: {state['query']}

Research findings:
{all_findings}

Available sources (use these for citations):
{sources_text}

Write a well-structured markdown report with:
1. Executive summary
2. Key findings (with inline citations using [1], [2] format)
3. Detailed analysis
4. Conclusion
5. Sources list at the end

Use inline citations [n] when referencing specific information."""
    
    response = llm.invoke(prompt)
    
    return {
        "report": response.content,
        "status": "completed"
    }


def should_continue(state: ResearchState) -> Literal["search", "synthesize"]:
    """Decide whether to continue searching or synthesize."""
    sub_queries_remaining = state["iteration"] < len(state["sub_queries"])
    
    if sub_queries_remaining and state["status"] != "synthesize":
        idx = min(state["iteration"], len(state["sub_queries"]) - 1)
        return {
            "current_sub_query": state["sub_queries"][idx],
            "next": "search"
        }
    return {"next": "synthesize"}


def build_graph() -> StateGraph:
    """Build the LangGraph research agent."""
    workflow = StateGraph(ResearchState)
    
    workflow.add_node("decompose", decompose_query)
    workflow.add_node("search", search_node)
    workflow.add_node("evaluate", evaluate_node)
    workflow.add_node("synthesize", synthesize_node)
    
    workflow.set_entry_point("decompose")
    
    workflow.add_edge("decompose", "search")
    workflow.add_edge("search", "evaluate")
    
    workflow.add_conditional_edges(
        "evaluate",
        should_continue,
        {
            "search": "search",
            "synthesize": "synthesize"
        }
    )
    
    workflow.add_edge("synthesize", END)
    
    return workflow.compile()


def run_research(query: str, max_iterations: int = 3) -> dict:
    """Execute a research query through the agent graph."""
    graph = build_graph()
    
    initial_state: ResearchState = {
        "query": query,
        "sub_queries": [],
        "current_sub_query": "",
        "findings": [],
        "sources": [],
        "iteration": 0,
        "max_iterations": max_iterations,
        "report": "",
        "status": "started",
        "error": ""
    }
    
    result = graph.invoke(initial_state)
    return result


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m src.agent.graph 'your research query'")
        sys.exit(1)
    
    query = " ".join(sys.argv[1:])
    print(f"Researching: {query}\n")
    
    result = run_research(query)
    
    print("=" * 60)
    print("RESEARCH REPORT")
    print("=" * 60)
    print(result["report"])
    print("\n" + "=" * 60)
    print(f"Sources used: {len(result['sources'])}")
