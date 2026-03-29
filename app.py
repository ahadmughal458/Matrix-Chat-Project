import streamlit as st
import json
import os
import numpy as np
import time
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from crypto_engine import HillCipher

# --- 1. CORE ENGINE SETUP ---
# Using your 3x3 Secret Key for Linear Algebra
secret_key = [[1, 2, 3], [0, 1, 4], [5, 6, 0]]
engine = HillCipher(secret_key)
DB_FILE = "chat_history.json"

def load_messages():
    if not os.path.exists(DB_FILE): return []
    try:
        with open(DB_FILE, "r") as f: return json.load(f)
    except: return []

def save_message(username, encrypted_matrix):
    messages = load_messages()
    messages.append({
        "user": username,
        "matrix": encrypted_matrix.tolist(),
        "time": datetime.now().strftime("%I:%M %p")
    })
    with open(DB_FILE, "w") as f: json.dump(messages, f)

# --- 2. PAGE CONFIG & HUMANIZED STYLING ---
st.set_page_config(page_title="Matrix Crypt", page_icon="🔐", layout="centered")

# Custom CSS for a professional, non-AI look
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); color: #E0E0E0; }
    .chat-bubble {
        padding: 15px;
        border-radius: 20px;
        margin-bottom: 15px;
        max-width: 85%;
        font-family: 'Inter', sans-serif;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .user-bubble { 
        background: linear-gradient(to right, #00c6ff, #0072ff); 
        color: white; 
        margin-left: auto; 
        border-bottom-right-radius: 2px; 
    }
    .other-bubble { 
        background: rgba(255, 255, 255, 0.1); 
        backdrop-filter: blur(10px);
        color: #f1f1f1; 
        margin-right: auto; 
        border-bottom-left-radius: 2px; 
        border: 1px solid rgba(255,255,255,0.1);
    }
    .metadata { font-size: 0.7rem; opacity: 0.6; margin-top: 8px; font-weight: bold; }
    .stTextInput > div > div > input { border-radius: 20px; padding: 10px 20px; }
    .stButton > button { border-radius: 20px; transition: 0.3s; }
    .stButton > button:hover { transform: scale(1.02); }
    </style>
""", unsafe_allow_html=True)

# --- 3. SESSION & OFFICIAL TEAM LOGIN ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Project Matrix: Secure Node")
    st.info("Authorized Personnel Only - Please authenticate.")
    
    with st.container():
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        
        if st.button("Decrypt & Enter", use_container_width=True):
            # 👥 OFFICIAL TEAM DATABASE
            users = {
                "tatheer fatima": "tatheer123",
                "maheen sabir": "maheen456",
                "sehris": "sehris789",
                "abdul aahad": "aahad000",
                "m ahmed": "ahmed111",
                "essa raza": "essa222",
                "admin": "professor99"
            }
            
            input_user = u.lower().strip()
            if input_user in users and users[input_user] == p:
                st.session_state.logged_in = True
                st.session_state.username = u.title()
                st.toast(f"Access Granted. Welcome, {u.title()}!", icon="✔️")
                time.sleep(1)
                st.rerun()
            else:
                st.error("🚨 Authentication Failed: Key Mismatch")
    st.stop()

# --- 4. THE LIVE CHAT INTERFACE ---
# Refresh logic (check every 1 second)
st_autorefresh(interval=1000, key="chatupdate")

# Header Section
c1, c2 = st.columns([5, 1])
with c1:
    st.markdown(f"### 📟 Node: {st.session_state.username}")
with c2:
    if st.button("Log Out"):
        st.session_state.logged_in = False
        st.rerun()

st.divider()

# Message Display Area
chat_placeholder = st.container()
messages = load_messages()

with chat_placeholder:
    for msg in messages:
        # Check if the current user is the one who sent the message
        is_me = (msg["user"].lower().strip() == st.session_state.username.lower().strip())
        
        # Check if the current user is the Admin (God-Mode check)
        is_admin = (st.session_state.username.lower().strip() == "admin")
        
        # Matrix Decryption
        try:
            decrypted_text = engine.decrypt(np.array(msg["matrix"]))
        except:
            decrypted_text = "[Decryption Error: Key mismatch]"
        
        bubble_type = "user-bubble" if is_me else "other-bubble"
        display_name = "You" if is_me else msg["user"]
        
        # 👑 GOD-MODE VIEW: If admin, build a special raw data block
        admin_data = ""
        if is_admin:
            # Convert the matrix list to a string for display
            raw_matrix = str(msg["matrix"])
            admin_data = f"""
            <div style="background: rgba(0, 0, 0, 0.4); border: 1px dashed #ff0055; padding: 10px; margin-top: 10px; border-radius: 5px; font-family: monospace; font-size: 0.75rem; color: #ff4b4b;">
                <strong>👑 GOD-MODE | RAW ENCRYPTED MATRIX:</strong><br>
                {raw_matrix}
            </div>
            """
        
        # Render the chat bubble (includes admin_data if applicable)
        st.markdown(f"""
            <div class="chat-bubble {bubble_type}">
                <div style="font-size: 0.8rem; font-weight: bold; margin-bottom: 3px;">{display_name}</div>
                {decrypted_text}
                {admin_data}
                <div class="metadata">{msg.get('time', 'Unknown')}</div>
            </div>
        """, unsafe_allow_html=True)

# Sticky Chat Input at the bottom
st.write("") # Padding
with st.container():
    with st.form("chat_input", clear_on_submit=True):
        cols = st.columns([4, 1])
        with cols[0]:
            user_msg = st.text_input("Enter secure message...", label_visibility="collapsed")
        with cols[1]:
            send_btn = st.form_submit_button("Send ➔", use_container_width=True)
            
        if send_btn and user_msg:
            # Linear Algebra Encryption: C = A * P
            encrypted_data = engine.encrypt(user_msg)
            save_message(st.session_state.username, encrypted_data)
            st.rerun()
