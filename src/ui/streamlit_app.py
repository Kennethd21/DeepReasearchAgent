"""Streamlit UI for the Deep Research Agent."""

import os
import json
from datetime import datetime
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Deep Research Agent",
    page_icon="🔬",
    layout="wide"
)

if "history" not in st.session_state:
    st.session_state.history = []
if "report" not in st.session_state:
    st.session_state.report = None
if "sources" not in st.session_state:
    st.session_state.sources = []


def save_outputs(query: str, report: str, sources: list):
    """Save report and sources to outputs directory."""
    outputs_dir = Path("outputs")
    outputs_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_query = "".join(c if c.isalnum() else "_" for c in query[:30])
    
    report_path = outputs_dir / f"{timestamp}_{safe_query}.md"
    report_path.write_text(report, encoding="utf-8")
    
    sources_path = outputs_dir / f"{timestamp}_{safe_query}_sources.json"
    sources_path.write_text(json.dumps(sources, indent=2), encoding="utf-8")
    
    return report_path, sources_path


def run_research(query: str, depth: str = "standard"):
    """Run research with progress updates."""
    from src.agent.graph import build_graph, decompose_query, search_node, evaluate_node, synthesize_node
    
    max_iter = 2 if depth == "quick" else 3
    
    graph = build_graph()
    
    initial_state = {
        "query": query,
        "sub_queries": [],
        "current_sub_query": "",
        "findings": [],
        "sources": [],
        "iteration": 0,
        "max_iterations": max_iter,
        "report": "",
        "status": "started",
        "error": ""
    }
    
    status_container = st.status("Researching...", expanded=True)
    
    try:
        with status_container:
            st.write("📋 Decomposing query into sub-queries...")
            state = decompose_query(initial_state)
            initial_state.update(state)
            
            sub_queries = state.get("sub_queries", [])
            for i, sq in enumerate(sub_queries, 1):
                st.write(f"  {i}. {sq}")
            
            for i, sub_q in enumerate(sub_queries[:max_iter]):
                st.write(f"\n🔍 Searching: {sub_q}")
                search_result = search_node(initial_state)
                initial_state.update(search_result)
                
                st.write(f"  ✓ Found {len(search_result.get('sources', []))} sources")
                
                eval_result = evaluate_node(initial_state)
                initial_state.update(eval_result)
                
                if eval_result.get("status") == "synthesize":
                    st.write("  ✓ Sufficient information gathered")
                    break
            
            st.write("\n📝 Synthesizing research report...")
            synth_result = synthesize_node(initial_state)
            initial_state.update(synth_result)
            
            status_container.update(label="Research complete!", state="complete")
        
        return initial_state
        
    except Exception as e:
        status_container.update(label=f"Error: {str(e)}", state="error")
        raise e


def main():
    st.title("🔬 Deep Research Agent")
    st.markdown("AI-powered research with cited sources using LangGraph + Gemini + Tavily")
    
    with st.sidebar:
        st.header("Settings")
        depth = st.selectbox(
            "Research Depth",
            ["quick", "standard"],
            index=1,
            help="Quick: 2 iterations, Standard: 3 iterations"
        )
        
        st.header("History")
        if st.session_state.history:
            for i, entry in enumerate(reversed(st.session_state.history[-5:])):
                st.caption(f"• {entry['query'][:40]}...")
        else:
            st.caption("No previous runs")
    
    with st.form("research_form"):
        query = st.text_area(
            "Research Query",
            placeholder="e.g., Compare the environmental impact of electric vs hydrogen vehicles",
            height=100
        )
        submitted = st.form_submit_button("Start Research", type="primary")
    
    if submitted and query:
        if not os.getenv("GEMINI_API_KEY") or not os.getenv("TAVILY_API_KEY"):
            st.error("Please set GEMINI_API_KEY and TAVILY_API_KEY in your .env file")
            return
        
        with st.spinner("Setting up research agent..."):
            result = run_research(query, depth)
        
        st.session_state.report = result.get("report", "")
        st.session_state.sources = result.get("sources", [])
        
        st.session_state.history.append({
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "report_length": len(result.get("report", ""))
        })
    
    if st.session_state.report:
        st.header("📄 Research Report")
        st.markdown(st.session_state.report)
        
        if st.session_state.sources:
            with st.expander("📎 Sources", expanded=False):
                for i, source in enumerate(st.session_state.sources, 1):
                    st.markdown(f"**[{i}] {source.get('title', 'Untitled')}**")
                    st.markdown(f"URL: {source.get('url', 'N/A')}")
                    st.markdown(f"_{source.get('snippet', '')[:200]}_")
                    st.divider()
        
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="📥 Download Report (Markdown)",
                data=st.session_state.report,
                file_name="research_report.md",
                mime="text/markdown"
            )
        with col2:
            sources_json = json.dumps(st.session_state.sources, indent=2)
            st.download_button(
                label="📥 Download Sources (JSON)",
                data=sources_json,
                file_name="sources.json",
                mime="application/json"
            )
        
        if st.button("💾 Save to outputs/ folder"):
            report_path, sources_path = save_outputs(
                st.session_state.history[-1]["query"] if st.session_state.history else "research",
                st.session_state.report,
                st.session_state.sources
            )
            st.success(f"Saved to {report_path}")


if __name__ == "__main__":
    main()
