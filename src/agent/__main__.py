"""Allow running agent as module: python -m src.agent"""

from .graph import run_research
import sys

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m src.agent 'your research query'")
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
