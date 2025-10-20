import os
import re
import time
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Mermaid: prefer streamlit-mermaid, fall back to a small HTML component
try:
    import streamlit_mermaid as stmd
    HAS_STMD = True
except Exception:
    HAS_STMD = False

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import ListSortOrder, MessageTextContent

# ------------- Config -------------
st.set_page_config(page_title="Azure Agent Chat with Mermaid", page_icon="🤖", layout="centered")

PROJECT_ENDPOINT = os.environ.get("PROJECT_ENDPOINT")
MODEL_DEPLOYMENT_NAME = os.environ.get("MODEL_DEPLOYMENT_NAME")
EXISTING_AGENT_ID = os.environ.get("AGENT_ID")

if not PROJECT_ENDPOINT or not MODEL_DEPLOYMENT_NAME:
    st.error(
        "Missing PROJECT_ENDPOINT and/or MODEL_DEPLOYMENT_NAME environment variables. "
        "Please set them and restart."
    )
    st.stop()

# ------------- Helpers -------------
def get_clients():
    """Create the AIProjectClient once and cache it."""
    if "project_client" not in st.session_state:
        st.session_state.project_client = AIProjectClient(
            endpoint=PROJECT_ENDPOINT,
            credential=DefaultAzureCredential()
        )
    return st.session_state.project_client, st.session_state.project_client.agents

def create_or_get_agent(agents_client):
    """Create an Agent the first time the app runs, or reuse an existing one if provided."""
    if "agent_id" in st.session_state:
        return st.session_state.agent_id

    if EXISTING_AGENT_ID:
        st.session_state.agent_id = EXISTING_AGENT_ID
        return EXISTING_AGENT_ID

    # Create a simple, reusable agent with default instructions
    agent = agents_client.create_agent(
        model=MODEL_DEPLOYMENT_NAME,
        name="streamlit-mermaid-agent",
        instructions=(
            "You are a helpful assistant. "
            "When appropriate, you may return Mermaid diagrams inside triple-backtick fenced blocks "
            "with the language identifier 'mermaid'. "
            "You may also return Markdown, text, or image links."
        )
    )
    st.session_state.agent_id = agent.id
    return agent.id

def get_or_create_thread(agents_client):
    if "thread_id" not in st.session_state:
        thread = agents_client.threads.create()
        st.session_state.thread_id = thread.id
        st.session_state.seen_message_ids = set()  # for incremental display
    return st.session_state.thread_id

MERMAID_REGEX = re.compile(r"```mermaid\s+([\s\S]*?)```", re.IGNORECASE)

def split_text_into_segments(text: str):
    """
    Split a text message into segments of {"type": "markdown"|"mermaid", "content": str}.
    """
    segments = []
    last_end = 0
    for m in MERMAID_REGEX.finditer(text):
        if m.start() > last_end:
            segments.append({"type": "markdown", "content": text[last_end:m.start()]})
        segments.append({"type": "mermaid", "content": m.group(1).strip()})
        last_end = m.end()
    if last_end < len(text):
        segments.append({"type": "markdown", "content": text[last_end:]})
    return segments

def render_mermaid(code: str, height: int = 480):
    """
    Render Mermaid using streamlit-mermaid if available, else via a small HTML component.
    """
    if HAS_STMD:
        stmd.st_mermaid(code)
        return
    # Fallback: inline mermaid.js (ESM) from CDN
    components.html(
        f"""
        <pre class="mermaid">{code}</pre>
        <script type="module">
            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
            mermaid.initialize({{ startOnLoad: true }});
        </script>
        """,
        height=height,
    )

def render_text_with_mermaid(text: str):
    """
    Render text that may contain: normal Markdown and ```mermaid``` fenced blocks.
    """
    segments = split_text_into_segments(text)
    for seg in segments:
        if seg["type"] == "markdown":
            if seg["content"].strip():
                st.markdown(seg["content"])
        else:  # mermaid
            render_mermaid(seg["content"])

def display_new_assistant_messages(agents_client, thread_id: str):
    """
    Fetch thread messages in ascending order and display only new 'assistant' messages.
    Handles text (incl. Mermaid) and images via markdown image URLs.
    """
    from azure.ai.agents.models import MessageImageFileContent  # doc ref: class exists
    messages = agents_client.messages.list(thread_id=thread_id, order=ListSortOrder.ASCENDING)

    for msg in messages:
        if msg.id in st.session_state.seen_message_ids:
            continue
        st.session_state.seen_message_ids.add(msg.id)

        if msg.role == "assistant":
            with st.chat_message("assistant"):
                # Each message can have multiple content parts (text, images, etc.)
                for part in msg.content:
                    # Text content
                    if isinstance(part, MessageTextContent):
                        render_text_with_mermaid(part.text.value)
                    # Image file content from the Agents service (advanced)
                    elif part.type == "image_file":
                        # The SDK exposes MessageImageFileContent with image_file.file_id.
                        # You can use the file_id to download bytes and show st.image,
                        # but that requires an extra call. For now, show a helpful note.
                        file_id = getattr(part.image_file, "file_id", None)
                        st.info(f"Agent returned an image file (id: {file_id}). "
                                "Downloading/rendering programmatically can be added as a next step.")
                    # Image via URL (if present)
                    elif getattr(part, "type", "") == "image_url":
                        url = getattr(getattr(part, "image_url", None), "url", None)
                        if url:
                            st.image(url, use_column_width=True)
                    else:
                        # Fallback: json-ish view
                        st.write(part)

# ------------- UI -------------
st.title("🤖 Azure Agent Chat + Mermaid")

if "history" not in st.session_state:
    st.session_state.history = []

project_client, agents_client = get_clients()
agent_id = create_or_get_agent(agents_client)
thread_id = get_or_create_thread(agents_client)

# show previous turns
for name, content in st.session_state.history:
    with st.chat_message(name):
        if name == "assistant":
            render_text_with_mermaid(content)
        else:
            st.markdown(content)

# input
user_prompt = st.chat_input("Type your message…")
if user_prompt:
    st.session_state.history.append(("user", user_prompt))
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # Send message to thread -> Run the agent -> Poll until complete
    agents_client.messages.create(thread_id=thread_id, role="user", content=user_prompt)
    run = agents_client.runs.create(thread_id=thread_id, agent_id=agent_id)

    with st.status("Thinking…", expanded=False):
        while run.status in ("queued", "in_progress", "requires_action"):
            time.sleep(0.7)
            run = agents_client.runs.get(thread_id=thread_id, run_id=run.id)

    # After run completes, fetch and display any new assistant messages
    display_new_assistant_messages(agents_client, thread_id)

st.caption(
    "Tip: To reuse an existing Agent across sessions, set the AGENT_ID env var. "
    "Otherwise this app creates an Agent for the session."
)