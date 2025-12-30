import os
import json
import time
import uuid
import streamlit as st
from datetime import datetime
from pathlib import Path
from google import genai
from google.genai import types

# --- CONFIGURATION ---
STORAGE_DIR = Path("research_history")
STORAGE_DIR.mkdir(exist_ok=True)
AGENT_NAME = "deep-research-pro-preview-12-2025"
SUMMARY_MODEL = "gemini-2.5-flash"

st.set_page_config(page_title="Gemini Deep Research Analyst", layout="wide")

# Initialize Gemini Client
if "client" not in st.session_state:
    st.session_state.client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

# --- DATA PERSISTENCE ---
def save_research_session(session_id, data):
    session_path = STORAGE_DIR / session_id
    session_path.mkdir(exist_ok=True)
    with open(session_path / "data.json", "w") as f:
        json.dump(data, f, indent=4)

def load_all_sessions():
    sessions = []
    for folder in STORAGE_DIR.iterdir():
        if folder.is_dir() and (folder / "data.json").exists():
            with open(folder / "data.json", "r") as f:
                sessions.append(json.load(f))
    return sorted(sessions, key=lambda x: x['timestamp'], reverse=True)

def generate_summary_and_title(prompt, result_text):
    try:
        summary_prompt = f"Summarize this research task in under 160 characters. Task: {prompt}\nResult: {result_text[:2000]}"
        response = st.session_state.client.models.generate_content(model=SUMMARY_MODEL, contents=summary_prompt)
        summary = response.text.strip()
        
        title_prompt = f"Give a 3-5 word title for this research: {prompt}"
        title_response = st.session_state.client.models.generate_content(model=SUMMARY_MODEL, contents=title_prompt)
        title = title_response.text.strip().replace('"', '')
        return title, summary
    except:
        return "New Research", prompt[:157] + "..."

# --- SIDEBAR & HISTORY ---
def sidebar_management():
    st.sidebar.title("🧬 Deep Research Control")
    
    st.sidebar.subheader("File Search Settings")
    use_file_search = st.sidebar.checkbox("Enable File Search", help="Give the agent access to your private data stores.")
    store_name = st.sidebar.text_input("File Store Name", placeholder="fileSearchStores/my-store", disabled=not use_file_search)
    
    st.sidebar.divider()
    st.sidebar.title("📚 Research History")
    sessions = load_all_sessions()
    
    for s in sessions:
        dt = datetime.fromisoformat(s['timestamp']).strftime("%m/%d %H:%M")
        with st.sidebar.expander(f"{dt} | {s['title']}"):
            st.write(f"_{s['summary']}_")
            if st.button("View Thread", key=s['id']):
                st.session_state.viewing_session = s['id']
                st.rerun()
    
    return use_file_search, store_name

# --- MAIN UI ---
def main_research_ui(use_files, store_name):
    st.title("🔬 Gemini 3 Deep Research")
    
    if "viewing_session" in st.session_state:
        render_session_view(st.session_state.viewing_session)
        if st.button("← Start New Research"):
            del st.session_state.viewing_session
            st.rerun()
        return

    query = st.chat_input("Enter your research objective...")
    
    if query:
        session_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        # Configure Tools
        tools = []
        if use_files and store_name:
            tools.append({
                "type": "file_search",
                "file_search_store_names": [store_name]
            })

        with st.status("Agent is planning research steps...", expanded=True) as status:
            try:
                # 1. Start Interaction
                stream = st.session_state.client.interactions.create(
                    input=query,
                    agent=AGENT_NAME,
                    background=True,
                    stream=True,
                    tools=tools if tools else None,
                    agent_config={"thinking_summaries": "auto"}
                )
                
                full_text = ""
                thoughts = []
                
                for chunk in stream:
                    if chunk.event_type == "content.delta":
                        if chunk.delta.type == "text":
                            full_text += chunk.delta.text
                            st.write(chunk.delta.text)
                        elif chunk.delta.type == "thought_summary":
                            thought = f"💭 {chunk.delta.content.text}"
                            thoughts.append(thought)
                            st.write(thought)
                    
                    if chunk.event_type == "interaction.complete":
                        status.update(label="Research Synthetic Complete!", state="complete")
                
                # 2. Finalize & Save
                title, summary = generate_summary_and_title(query, full_text)
                session_data = {
                    "id": session_id,
                    "timestamp": timestamp,
                    "title": title,
                    "summary": summary,
                    "prompt": query,
                    "response": full_text,
                    "thoughts": thoughts,
                    "history": [{"role": "user", "text": query}, {"role": "agent", "text": full_text}]
                }
                save_research_session(session_id, session_data)
                st.rerun()
                
            except Exception as e:
                st.error(f"Research failed: {e}")

def render_session_view(session_id):
    session_path = STORAGE_DIR / session_id / "data.json"
    with open(session_path, "r") as f:
        data = json.load(f)
        
    st.header(data['title'])
    st.caption(f"Started: {data['timestamp']} | ID: {data['id']}")
    
    # Render the Thread
    for msg in data.get('history', []):
        with st.chat_message(msg['role']):
            st.markdown(msg['text'])
            if msg['role'] == "agent" and 'thoughts' in data:
                with st.expander("View Research Reasoning"):
                    for t in data['thoughts']:
                        st.write(t)

    # Follow up
    follow_up = st.chat_input("Ask a follow-up question about this report...")
    if follow_up:
        with st.spinner("Agent is elaborating..."):
            try:
                # Follow ups use gemini-3-pro-preview via previous_interaction_id
                response = st.session_state.client.interactions.create(
                    input=follow_up,
                    model="gemini-3-pro-preview",
                    previous_interaction_id=data['id']
                )
                new_text = response.outputs[-1].text
                data['history'].append({"role": "user", "text": follow_up})
                data['history'].append({"role": "agent", "text": new_text})
                save_research_session(session_id, data)
                st.rerun()
            except Exception as e:
                st.error(f"Follow-up failed: {e}")

# --- EXECUTION ---
use_files, store_name = sidebar_management()
main_research_ui(use_files, store_name)
