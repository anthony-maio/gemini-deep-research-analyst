# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Streamlit-based web application wrapping Google's Gemini Deep Research API (`deep-research-pro-preview-12-2025`). The Deep Research Agent autonomously plans, executes, and synthesizes multi-step research tasks using web search and optional file search, producing detailed cited reports.

## Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Set API key (required before running)
# Windows PowerShell:
$env:GOOGLE_API_KEY='your_key_here'
# Windows cmd:
set GOOGLE_API_KEY=your_key_here
# Linux/Mac:
export GOOGLE_API_KEY='your_key_here'

# Run the application
streamlit run research_app.py
```

Streamlit hot-reloads on file changes during development.

## Architecture

Single-file application (`research_app.py`, ~180 lines) with these layers:

**Configuration** (top of file): Agent name, summary model, storage directory constants.

**Data Persistence**: JSON files stored in `research_history/[uuid]/data.json` with structure:
- `id`, `timestamp`, `title`, `summary`, `prompt`, `response`
- `thoughts[]` - agent reasoning captured during streaming
- `history[]` - follow-up conversation turns

**AI Integration**:
- Primary: `interactions.create()` with `background=True, stream=True` for async deep research
- Secondary: Gemini 2.5 Flash for auto-generating titles/summaries
- Follow-ups: Use `previous_interaction_id` to continue conversations

**UI Components** (Streamlit):
- `sidebar_management()`: History list, file search toggle
- `main_research_ui()`: Chat input, streaming display
- `render_session_view()`: View saved sessions, follow-up Q&A

## Key API Patterns

```python
# Streaming research with thought capture
stream = client.interactions.create(
    input=query,
    agent="deep-research-pro-preview-12-2025",
    background=True,
    stream=True,
    agent_config={"thinking_summaries": "auto"},
    tools=[{"type": "file_search", "file_search_store_names": [...]}]  # optional
)

# Event types: "content.delta" (text/thought_summary), "interaction.complete"

# Follow-up without re-running research
client.interactions.create(
    input=follow_up,
    model="gemini-3-pro-preview",
    previous_interaction_id=session_id
)
```

## Dependencies

- `streamlit` - Web UI framework
- `google-genai` - Google Generative AI SDK (Interactions API)
- `pydantic` - Data validation (imported but unused currently)
