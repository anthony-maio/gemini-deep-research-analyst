# Gemini Deep Research Analyst

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.0+-FF4B4B.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Streamlit-based "Analyst Workspace" for Google's **Gemini Deep Research API**. The Deep Research Agent autonomously plans, executes, and synthesizes multi-step research tasks—navigating the web and your own data to produce detailed, cited reports.

> **Note:** The Deep Research Agent is currently in preview and exclusively available through the [Interactions API](https://ai.google.dev/gemini-api/docs/interactions).

## Features

- **Real-time Streaming** — Watch the agent's progress with live thought summaries as it searches and synthesizes
- **Automatic Cataloging** — Gemini 2.5 Flash generates concise titles and summaries for each research session
- **Persistent History** — All research (prompts, outputs, reasoning) saved as JSON for future reference
- **Follow-up Questions** — Continue conversations about completed research without re-running the full search
- **File Search Integration** — Combine web search with your private documents from Google AI Studio
- **Reasoning Transparency** — View the agent's internal thinking process that led to conclusions

## Quick Start

### Prerequisites

- Python 3.8+
- A [Google AI API key](https://aistudio.google.com/apikey)

### Installation

```bash
# Clone the repository
git clone https://github.com/anthonymaio/gemini-deep-research-analyst.git
cd gemini-deep-research-analyst

# Install dependencies
pip install -r requirements.txt

# Set your API key
export GOOGLE_API_KEY='your_key_here'  # Linux/Mac
# or
$env:GOOGLE_API_KEY='your_key_here'    # Windows PowerShell

# Run the app
streamlit run research_app.py
```

The app will open in your browser at `http://localhost:8501`.

## Usage

### Basic Research

1. Enter your research query in the chat input
2. Watch real-time progress as the agent searches and analyzes
3. View the final report with citations
4. Ask follow-up questions about the research

### Using File Search

To include your own documents in research:

1. Create a File Store in [Google AI Studio](https://aistudio.google.com/) and upload your documents
2. Toggle **"Enable File Search"** in the sidebar
3. Enter your store name (e.g., `fileSearchStores/my-docs`)
4. Run your query — the agent will prioritize your private data alongside web results

## How It Works

```
User Query → Deep Research Agent (background=True, stream=True)
                    ↓
        [Plan → Search → Read → Iterate]
                    ↓
        Real-time thought summaries displayed
                    ↓
        Final report with citations
                    ↓
        Gemini 2.5 Flash generates title/summary
                    ↓
        Session saved to research_history/[uuid]/data.json
```

## Project Structure

```
├── research_app.py      # Main Streamlit application
├── requirements.txt     # Python dependencies
├── research_history/    # Persisted research sessions (auto-created)
└── CLAUDE.md           # AI assistant guidance
```

## Configuration

| Environment Variable | Required | Description |
|---------------------|----------|-------------|
| `GOOGLE_API_KEY` | Yes | Your Google AI API key |

## API Reference

This application uses:
- **Deep Research Agent**: `deep-research-pro-preview-12-2025`
- **Summary Model**: `gemini-2.5-flash`
- **Follow-up Model**: `gemini-3-pro-preview`

See the [Gemini Deep Research documentation](https://ai.google.dev/gemini-api/docs/deep-research) for more details.

## Limitations

- Research tasks can take several minutes (up to 60 minutes max)
- Audio inputs are not supported
- Custom function calling tools cannot be added to the agent
- The preview may have rate limits

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Powered by [Google Gemini](https://ai.google.dev/)
