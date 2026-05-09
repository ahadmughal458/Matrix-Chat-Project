import streamlit as st
import json
import os
import numpy as np
from crypto_engine import HillCipher
from streamlit_autorefresh import st_autorefresh
from github import Github
from github.GithubException import GithubException
from datetime import datetime

# ------------------------------
# Page config
# ------------------------------
st.set_page_config(
    page_title="CHAT APP BY CODECREATIFY",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ------------------------------
# Custom CSS – clean, modern, light mode
# ------------------------------
light_css = """
<style>
    /* Remove default Streamlit padding and margins */
    .main > div {
        padding: 0rem 1rem;
    }
    a._container_gzau3_1._viewerBadge_nim44_23 {
    display: none;
}
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        max-width: 800px;
        margin: 0 auto;
    }
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Global font */
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        background-color: #f5f7fb;
    }
    
    /* Chat message container */
    .chat-message {
        display: flex;
        margin-bottom: 1rem;
        align-items: flex-start;
    }
    .chat-message.user {
        justify-content: flex-end;
    }
    a._container_gzau3_1._viewerBadge_nim44_23 {
    display: none;
    }
    .chat-message.other {
        justify-content: flex-start;
    }
    /* Avatar */
    .avatar {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background-color: #e4e6eb;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        margin-right: 12px;
        flex-shrink: 0;
        color: #4a4a4a;
    }
    .user .avatar {
        order: 2;
        margin-left: 12px;
        margin-right: 0;
        background-color: #0084ff;
        color: white;
    }
    /* Bubble */
    .bubble {
        max-width: 70%;
        padding: 10px 14px;
        border-radius: 18px;
        font-size: 14px;
        line-height: 1.4;
        word-wrap: break-word;
        box-shadow: 0 1px 1px rgba(0,0,0,0.05);
    }
    .user .bubble {
        background-color: #0084ff;
        color: white;
        border-bottom-right-radius: 4px;
    }
    .other .bubble {
        background-color: #ffffff;
        color: #1c1e21;
        border: 1px solid #e4e6eb;
        border-bottom-left-radius: 4px;
    }
    /* Timestamp */
    .timestamp {
        font-size: 11px;
        color: #8a8d91;
        margin: 4px 8px 0;
    }
    .user .timestamp {
        text-align: right;
    }
    /* Header */
    .chat-header {
        background-color: white;
        border-bottom: 1px solid #e4e6eb;
        padding: 12px 20px;
        position: sticky;
        top: 0;
        z-index: 100;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .chat-title {
        font-weight: 600;
        font-size: 18px;
    }
    .logout-btn {
        background: none;
        border: none;
        color: #0084ff;
        font-weight: 500;
        cursor: pointer;
    }
    /* Input area */
    .stChatInput > div > div > textarea {
        background-color: white;
        border-radius: 24px;
        border: 1px solid #e4e6eb;
        padding: 10px 16px;
        font-size: 14px;
    }
    .stChatInput > div > div > textarea:focus {
        border-color: #0084ff;
        box-shadow: 0 0 0 2px rgba(0,132,255,0.2);
    }
    /* Button */
    div.stButton > button {
        background-color: #0084ff;
        color: white;
        border-radius: 24px;
        border: none;
        padding: 0.3rem 1rem;
        font-weight: 500;
    }
    /* Admin panel (softer) */
    .admin-badge {
        background-color: #f0f2f5;
        border-radius: 12px;
        padding: 8px 12px;
        font-size: 12px;
        font-family: monospace;
        margin: 8px 0;
        color: #4b4f54;
    }
</style>
"""
st.markdown(light_css, unsafe_allow_html=True)

# ------------------------------
# Config
# ------------------------------
secret_key = [
    [1, 2, 3],
    [0, 1, 4],
    [5, 6, 0]
]
engine = HillCipher(secret_key)
DB_FILE = "chat_history.json"

GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", "")
REPO_NAME = st.secrets.get("REPO_NAME", "")
GITHUB_FILE_PATH = "chat_history.json"

# ------------------------------
# DB functions
# ------------------------------
def load_messages():
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, "r") as f:
        return json.load(f)

def push_to_github():
    if not GITHUB_TOKEN or not REPO_NAME:
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
    except Exception:
        pass

def save_message(username, encrypted_matrix):
    msgs = load_messages()
    msgs.append({
        "user": username,
        "matrix": encrypted_matrix.tolist(),
        "ts": datetime.now().strftime("%I:%M %p")
    })
    with open(DB_FILE, "w") as f:
        json.dump(msgs, f)
    push_to_github()

# ------------------------------
# Auth
# ------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

users = {
    "ahad": "ahad123",
    "admin": "admin123",
    "essa": "essa123",
    "ahmed": "ahmed123",
    "sehrish": "sehrish123",
    "maheen": "maheen123"
}

# ------------------------------
# Login screen (clean)
# ------------------------------
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/906/906324.png", width=80)
        st.markdown("<h2 style='text-align:center;'>Matrix Chat</h2>", unsafe_allow_html=True)
        with st.form("login"):
            username = st.text_input("Username", placeholder="e.g. ahad")
            password = st.text_input("Password", type="password", placeholder="••••••")
            if st.form_submit_button("Log in", use_container_width=True):
                if username in users and users[username] == password:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("Wrong username or password")
        st.caption("🔐 End-to-end encrypted with Hill cipher")

# ------------------------------
# Main chat UI
# ------------------------------
else:
    st_autorefresh(interval=2000, limit=None, key="refresh")
    
    # Header
    col1, col2 = st.columns([3,1])
    with col1:
        st.markdown("<div class='chat-title'>💬 Matrix Chat</div>", unsafe_allow_html=True)
    with col2:
        if st.button("Logout", key="logout_btn"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()
    
    st.markdown("<hr style='margin:0 0 1rem 0;'>", unsafe_allow_html=True)
    
    # Chat history display
    chat_container = st.container()
    with chat_container:
        msgs = load_messages()
        for m in msgs:
            sender = m["user"]
            matrix = np.array(m["matrix"])
            decrypted = engine.decrypt(matrix)
            ts = m.get("ts", "")
            
            # Admin sees raw matrix in a subtle way
            if st.session_state.username == "admin":
                st.markdown(f"""
                <div class='admin-badge'>
                    <strong>🕵️ Intercepted from {sender}</strong> · {ts}<br>
                    <span style='font-size:11px;'>Matrix: {matrix.tolist()}</span><br>
                    <strong>Decrypted:</strong> {decrypted}
                </div>
                """, unsafe_allow_html=True)
            else:
                # Normal chat bubbles
                if sender == st.session_state.username:
                    st.markdown(f"""
                    <div class='chat-message user'>
                        <div style='text-align:right;'>
                            <div class='bubble'>{decrypted}</div>
                            <div class='timestamp'>{ts}</div>
                        </div>
                        <div class='avatar'>{sender[0].upper()}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class='chat-message other'>
                        <div class='avatar'>{sender[0].upper()}</div>
                        <div>
                            <div class='bubble'>{decrypted}</div>
                            <div class='timestamp'>{sender} · {ts}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    
    # Input box
    new_msg = st.chat_input("Type a message...")
    if new_msg and new_msg.strip():
        enc = engine.encrypt(new_msg.strip())
        save_message(st.session_state.username, enc)
        st.rerun()
