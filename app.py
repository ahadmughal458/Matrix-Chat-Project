import streamlit as st
import json
import os
import numpy as np
from crypto_engine import HillCipher
from streamlit_autorefresh import st_autorefresh
from github import Github
from github.GithubException import GithubException
from datetime import datetime

# ==========================================
# 1. CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Matrix Chat",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide default Streamlit elements
hide_st_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp {margin-top: -50px;}
    </style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# Custom CSS for chat bubbles, background, fonts
custom_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    }
    
    .chat-container {
        background: rgba(20, 20, 40, 0.6);
        border-radius: 20px;
        padding: 20px;
        backdrop-filter: blur(10px);
        margin-bottom: 20px;
    }
    
    .user-bubble {
        background: #00c6ff;
        background: linear-gradient(135deg, #00c6ff, #0072ff);
        color: white;
        border-radius: 20px 20px 5px 20px;
        padding: 10px 18px;
        display: inline-block;
        max-width: 70%;
        margin: 8px 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        font-weight: 500;
    }
    
    .other-bubble {
        background: #2c2c3e;
        color: #f0f0f0;
        border-radius: 20px 20px 20px 5px;
        padding: 10px 18px;
        display: inline-block;
        max-width: 70%;
        margin: 8px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .admin-bubble {
        background: #ff416c;
        background: linear-gradient(135deg, #ff4b2b, #ff416c);
        color: white;
        border-radius: 20px 5px 20px 20px;
        padding: 10px 18px;
        font-family: monospace;
        font-size: 0.85rem;
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #00c6ff, #0072ff);
        color: white;
        border: none;
        border-radius: 30px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 5px 15px rgba(0,114,255,0.4);
    }
    
    .stTextInput > div > div > input {
        background: rgba(255,255,255,0.1);
        border-radius: 30px;
        color: white;
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    .stChatInput > div > div > textarea {
        background: rgba(30,30,50,0.9);
        border-radius: 30px;
        color: white;
        border: 1px solid #00c6ff;
    }
    
    .timestamp {
        font-size: 0.7rem;
        color: #aaa;
        margin-left: 12px;
    }
    
    .welcome-header {
        background: rgba(0,198,255,0.15);
        padding: 1rem;
        border-radius: 30px;
        text-align: center;
        backdrop-filter: blur(5px);
        margin-bottom: 20px;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# Key & GitHub (use environment variables if possible)
secret_key = [
    [1, 2, 3],
    [0, 1, 4],
    [5, 6, 0]
]
engine = HillCipher(secret_key)
DB_FILE = "chat_history.json"

GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", "YOUR_TOKEN")
REPO_NAME = st.secrets.get("REPO_NAME", "user/repo")
GITHUB_FILE_PATH = "chat_history.json"

# ==========================================
# 2. DATABASE FUNCTIONS
# ==========================================
def load_messages():
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, "r") as f:
        return json.load(f)

def push_to_github():
    if GITHUB_TOKEN == "YOUR_TOKEN":
        return
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)
        with open(DB_FILE, 'r') as f:
            content = f.read()
        try:
            contents = repo.get_contents(GITHUB_FILE_PATH)
            repo.update_file(contents.path, "Chat update", content, contents.sha)
        except GithubException:
            repo.create_file(GITHUB_FILE_PATH, "Initial chat", content)
    except Exception as e:
        st.toast(f"⚠️ GitHub sync failed: {e}", icon="⚠️")

def save_message(username, encrypted_matrix):
    messages = load_messages()
    messages.append({
        "user": username,
        "matrix": encrypted_matrix.tolist(),
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })
    with open(DB_FILE, "w") as f:
        json.dump(messages, f, indent=2)
    push_to_github()

# ==========================================
# 3. AUTHENTICATION
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

valid_users = {
    "ahad": "ahad123",
    "admin": "admin123",
    "essa": "essa123",
    "ahmed": "ahmed123",
    "sehrish": "sehrish123",
    "maheen": "maheen123"
}

# ==========================================
# 4. UI: LOGIN SCREEN (custom style)
# ==========================================
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div class='welcome-header'><h1 style='color:white;'>🔐 Matrix Chat</h1><p style='color:#ccc;'>Encrypted • Decentralized • Retro‑futuristic</p></div>", unsafe_allow_html=True)
        with st.form("login_form"):
            user_input = st.text_input("👤 Username", placeholder="Enter your username")
            pass_input = st.text_input("🔑 Password", type="password", placeholder="••••••")
            submitted = st.form_submit_button("🚀 Enter Chat Room")
            if submitted:
                if user_input in valid_users and valid_users[user_input] == pass_input:
                    st.session_state.logged_in = True
                    st.session_state.username = user_input
                    st.rerun()
                else:
                    st.error("❌ Access denied. Check your credentials.")
        st.markdown("<p style='text-align:center;color:#aaa;margin-top:40px;'>⚡ Hill cipher | Real‑time refresh | GitHub backup</p>", unsafe_allow_html=True)

# ==========================================
# 5. MAIN CHAT ROOM
# ==========================================
else:
    st_autorefresh(interval=2000, limit=None, key="chat_refresh")
    
    # Sidebar with user info
    with st.sidebar:
        st.markdown(f"### 👋 {st.session_state.username}")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()
        st.divider()
        st.caption("🔒 End‑to‑end encrypted with Hill cipher (3x3 matrix)")
        st.caption("📁 History saved locally + GitHub")
        if st.session_state.username == "admin":
            st.warning("🕵️ Admin mode: raw matrix visible")
    
    st.markdown("<div class='welcome-header'><h2>💬 Global CipherChat</h2><p>Messages are encrypted before storage — only the right key reveals them.</p></div>", unsafe_allow_html=True)
    
    # Display chat messages
    chat_history = load_messages()
    chat_container = st.container()
    with chat_container:
        for msg in chat_history:
            sender = msg["user"]
            matrix_data = np.array(msg["matrix"])
            decrypted = engine.decrypt(matrix_data)
            ts = msg.get("timestamp", "")
            
            if st.session_state.username == "admin":
                # Admin: show both matrix and plaintext
                with st.chat_message(name="assistant", avatar="🕵️"):
                    st.markdown(f"**Intercepted from `{sender}`** <span class='timestamp'>{ts}</span>", unsafe_allow_html=True)
                    st.code(f"Matrix:\n{matrix_data}", language="json")
                    st.markdown(f"<div class='admin-bubble'>🔓 {decrypted}</div>", unsafe_allow_html=True)
            else:
                # Regular user
                if sender == st.session_state.username:
                    with st.chat_message("user"):
                        st.markdown(f"<div class='user-bubble'>{decrypted}</div><span class='timestamp'>{ts}</span>", unsafe_allow_html=True)
                else:
                    with st.chat_message("assistant"):
                        st.markdown(f"**{sender}** <span class='timestamp'>{ts}</span>", unsafe_allow_html=True)
                        st.markdown(f"<div class='other-bubble'>{decrypted}</div>", unsafe_allow_html=True)
    
    # Input area
    new_msg = st.chat_input("✏️ Type your secret message...")
    if new_msg and new_msg.strip():
        encrypted = engine.encrypt(new_msg)
        save_message(st.session_state.username, encrypted)
        st.rerun()
