import streamlit as st
import uuid
import os
from datetime import datetime
from pymongo import MongoClient
from langchain_core.messages import AIMessageChunk
from agent import SupervisorRunner, Context
from dotenv import load_dotenv
load_dotenv()
# -------------------------------------------------------
# MongoDB
# -------------------------------------------------------
Mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "chat_db"

mongo = MongoClient(Mongo_uri)
db = mongo[DB_NAME]
chat_collection = db["chat_history"]

# -------------------------------------------------------
# Page Config
# -------------------------------------------------------
st.set_page_config(
    page_title="📈 Stock Market Multi-Agent Chat",
    page_icon="🤖",
    layout="wide",
)

st.title("🤖 Stock Market Multi-Agent Assistant")

# -------------------------------------------------------
# Session State
# -------------------------------------------------------
if "user_name" not in st.session_state:
    st.session_state.user_name = "Trader"

if "active_session" not in st.session_state:
    st.session_state.active_session = None

if "sessions" not in st.session_state:
    st.session_state.sessions = []


# -------------------------------------------------------
# Helpers
# -------------------------------------------------------
def load_sessions():
    sessions = chat_collection.find(
        {}, {"session_id": 1, "created_at": 1}
    ).sort("created_at", -1)
    return list(sessions)


def load_messages(session_id):
    doc = chat_collection.find_one({"session_id": session_id})
    if not doc:
        return []

    messages = []
    for day in sorted(doc.get("messages", {})):
        for m in doc["messages"][day]:
            messages.append({"role": "user", "content": m["prompt"]})
            messages.append({"role": "assistant", "content": m["answer"]})
    return messages


def new_session():
    sid = str(uuid.uuid4())
    st.session_state.active_session = sid
    st.rerun()


# -------------------------------------------------------
# Sidebar — Sessions + User
# -------------------------------------------------------
with st.sidebar:
    st.header("🧑 User")

    st.session_state.user_name = st.text_input(
        "Name", value=st.session_state.user_name
    )

    st.divider()

    st.header("💬 Chat Sessions")

    if st.button("➕ New Session"):
        new_session()

    st.session_state.sessions = load_sessions()

    for s in st.session_state.sessions:
        label = f"Session • {s['created_at'][:10]}"
        if st.button(label, key=s["session_id"]):
            st.session_state.active_session = s["session_id"]
            st.rerun()

# -------------------------------------------------------
# Main Layout
# -------------------------------------------------------
col_chat, col_tools = st.columns([4, 1])

# -------------------------------------------------------
# Chat History
# -------------------------------------------------------
with col_chat:
    if not st.session_state.active_session:
        st.info("Select a session or create a new one.")
    else:
        history = load_messages(st.session_state.active_session)

        for msg in history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

# -------------------------------------------------------
# Chat Input
# -------------------------------------------------------
if st.session_state.active_session:
    prompt = st.chat_input("Ask about stocks, trends, risks, analysis…")

    if prompt:
        with col_chat:
            with st.chat_message("user"):
                st.markdown(prompt)

        runner = SupervisorRunner(
            input_text=prompt,
            user_name=st.session_state.user_name,
            session_id=st.session_state.active_session,
        )

        with col_chat:
            with st.chat_message("assistant"):
                final_answer = st.write_stream(runner._run_graph_sync)

        st.rerun()

# -------------------------------------------------------
# Tool Activity (placeholder – future use)
# -------------------------------------------------------
with col_tools:
    st.markdown("### 🔧 Agent Notes")
    st.caption("Tool execution visible here in future builds.")
