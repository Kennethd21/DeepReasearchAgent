# Deep Research Agent

AI-powered research agent that uses LangGraph, Gemini, and Tavily to perform iterative web research and produce cited reports.

## Architecture

```
Query → Decompose → [Search → Evaluate] → Synthesize → Report
                         ↑         |
                         └─────────┘
                    (continue if needed)
```

### Components

- **LangGraph StateGraph**: Manages the ReAct research loop
- **Gemini 1.5 Flash**: LLM for query decomposition, evaluation, and synthesis
- **Tavily API**: Web search with structured results
- **Streamlit**: Interactive web UI with progress tracking

## Setup

### Prerequisites

- Python 3.11+
- API keys from:
  - [Google AI Studio](https://aistudio.google.com) (Gemini)
  - [Tavily](https://tavily.com) (Search)

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd deep-research-agent

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Usage

**CLI Mode:**
```bash
python -m src.agent "Your research query here"
```

**Web UI:**
```bash
python -m src.ui
# or
streamlit run src/ui/streamlit_app.py
```

## Project Structure

```
deep-research-agent/
├── src/
│   ├── agent/
│   │   ├── graph.py        # LangGraph StateGraph + nodes
│   │   ├── state.py        # TypedDict state schema
│   │   └── tools.py        # Tavily search integration
│   └── ui/
│       └── streamlit_app.py
├── outputs/                # Generated reports
├── .env                    # API keys (gitignored)
├── requirements.txt
└── README.md
```

## Features

- **Query Decomposition**: Breaks complex queries into sub-queries
- **Iterative Research**: Continues searching until sufficient data gathered
- **Cited Reports**: Markdown with inline citations [1], [2]
- **Multiple Outputs**: Download as Markdown or JSON
- **Research History**: Track previous runs in sidebar

## Rate Limits

- Tavily: 1000 credits/month free tier
- Each search uses 1 credit
- Default max 3 iterations per query

## License

MIT
