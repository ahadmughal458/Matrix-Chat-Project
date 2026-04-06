import streamlit as st
import json
import os
import numpy as np
from crypto_engine import HillCipher
from streamlit_autorefresh import st_autorefresh
from github import Github  # <-- NEW: Used for GitHub integration
from github.GithubException import GithubException

# ==========================================
# 1. SETUP THE MATH ENGINE & CONFIG
# ==========================================
secret_key = [
    [1, 2, 3],
    [0, 1, 4],
    [5, 6, 0]
]
engine = HillCipher(secret_key)
DB_FILE = "chat_history.json"

# --- GITHUB CONFIGURATION ---
# Replace these with your actual details!
GITHUB_TOKEN = "YOUR_GITHUB_PERSONAL_ACCESS_TOKEN" 
REPO_NAME = "your-username/your-repo-name"  
GITHUB_FILE_PATH = "chat_history.json" 

# ==========================================
# 2. DATABASE & GITHUB FUNCTIONS
# ==========================================
def load_messages():
    """Reads the encrypted matrices from our JSON file"""
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, "r") as f:
        return json.load(f)

def push_to_github():
    """Pushes the local chat_history.json to your GitHub repository"""
    if GITHUB_TOKEN == "YOUR_GITHUB_PERSONAL_ACCESS_TOKEN":
        return # Skip if token isn't set up yet
        
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)
        
        # Read the local file
        with open(DB_FILE, 'r') as file:
            content = file.read()

        try:
            # Try to update the file if it already exists
            contents = repo.get_contents(GITHUB_FILE_PATH)
            repo.update_file(
                contents.path, 
                "Automated chat history update", 
                content, 
                contents.sha
            )
        except GithubException:
            # If the file doesn't exist, create it
            repo.create_file(
                GITHUB_FILE_PATH, 
                "Initial chat history commit", 
                content
            )
    except Exception as e:
        st.error(f"GitHub Sync Error: {e}")

def save_message(username, encrypted_matrix):
    """Saves a new encrypted matrix locally, then pushes to GitHub"""
    messages = load_messages()
    messages.append({
        "user": username,
        "matrix": encrypted_matrix.tolist()
    })
    
    # 1. Save Locally
    with open(DB_FILE, "w") as f:
        json.dump(messages, f)
        
    # 2. Push to GitHub
    push_to_github()

# ==========================================
# 3. SESSION STATE (Remembering the User)
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# Allowed Users
valid_users = {
    "ahad": "ahad123",
    "admin": "admin123",
    "essa": "essa123",
    "ahmed123": "ahmed123",
    "maheen": "maheen123"
}

# ==========================================
# 4. THE WEB INTERFACE
# ==========================================
st.set_page_config(page_title="Matrix Chat")

# --- SCREEN A: LOGIN SYSTEM ---
if not st.session_state.logged_in:
    st.title("Login Page")
    st.write("Please log in to access.")
    
    user_input = st.text_input("Username")
    pass_input = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if user_input in valid_users and valid_users[user_input] == pass_input:
            st.session_state.logged_in = True
            st.session_state.username = user_input
            st.rerun() 
        else:
            st.error("❌ Invalid Username or Password")

# --- SCREEN B: THE CHAT ROOM ---
else:
    # AUTO-REFRESH MAGIC
    # Set to 1000ms (1 second). Going faster than this will likely crash Streamlit.
    st_autorefresh(interval=1000, limit=None, key="chat_autorefresh")

    st.title("Global Matrix Chat")
    
    # Header layout
    col1, col2 = st.columns([0.8, 0.2])
    with col1:
        st.write(f"Welcome to the secure server, **{st.session_state.username}**.")
    with col2:
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()

    st.divider()

    # 1. Display all past messages
    st.subheader("Live Chat")
    chat_history = load_messages()
    
    for msg in chat_history:
        sender = msg["user"]
        matrix_data = np.array(msg["matrix"])
        
        # Decrypt for the UI
        decrypted_text = engine.decrypt(matrix_data)
        
        # --- ADMIN "HACKER" VIEW ---
        if st.session_state.username == "admin":
            with st.chat_message("assistant", avatar="🕵️"):
                st.caption(f"Intercepted from: {sender}")
                st.code(f"Raw Matrix Data:\n{matrix_data}", language="json")
                st.write(f"**Decrypted:** {decrypted_text}")
                
        # --- REGULAR USER VIEW ---
        else:
            if sender == st.session_state.username:
                st.chat_message("user").write(f"**You:** {decrypted_text}")
            else:
                st.chat_message("assistant").write(f"**{sender}:** {decrypted_text}")
            
    # 2. Input box for new messages
    new_message = st.chat_input("Type your secret message here...")
    if new_message:
        encrypted_data = engine.encrypt(new_message)
        save_message(st.session_state.username, encrypted_data)
        st.rerun()
