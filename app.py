import streamlit as st
import json
import os
import numpy as np
from crypto_engine import HillCipher

# ==========================================
# 1. SETUP THE MATH ENGINE & DATABASE
# ==========================================
secret_key = [
    [1, 2, 3],
    [0, 1, 4],
    [5, 6, 0]
]
engine = HillCipher(secret_key)
DB_FILE = "chat_history.json"

# ==========================================
# 2. DATABASE FUNCTIONS
# ==========================================
def load_messages():
    """Reads the encrypted matrices from our JSON file"""
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_message(username, encrypted_matrix):
    """Saves a new encrypted matrix to our JSON file"""
    messages = load_messages()
    messages.append({
        "user": username,
        "matrix": encrypted_matrix.tolist()
    })
    with open(DB_FILE, "w") as f:
        json.dump(messages, f)

# ==========================================
# 3. SESSION STATE (Remembering the User)
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# Allowed Users
valid_users = {
    "ahad": "secure123",
    "admin": "password123",
    "professor": "mathrocks"
}

# ==========================================
# 4. THE WEB INTERFACE
# ==========================================
st.set_page_config(page_title="Matrix Chat", page_icon="🕶️")

# --- SCREEN A: LOGIN SYSTEM ---
if not st.session_state.logged_in:
    st.title("🔒 Secure Matrix Login")
    st.write("Please log in to access the encrypted server.")
    
    user_input = st.text_input("Username")
    pass_input = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if user_input in valid_users and valid_users[user_input] == pass_input:
            st.session_state.logged_in = True
            st.session_state.username = user_input
            st.rerun() # Refresh the page to show the chat!
        else:
            st.error("❌ Invalid Username or Password")

# --- SCREEN B: THE CHAT ROOM ---
else:
    st.title("🕶️ Global Matrix Chat")
    st.write(f"Welcome to the secure server, **{st.session_state.username}**.")
    
    # Logout Button
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
        
        # Math Magic: Decrypt it on the fly!
        decrypted_text = engine.decrypt(matrix_data)
        
        # Show it nicely in the UI
        if sender == st.session_state.username:
            st.chat_message("user").write(f"**You:** {decrypted_text}")
        else:
            st.chat_message("assistant").write(f"**{sender}:** {decrypted_text}")
            
    # Refresh button to see if the other person replied
    if st.button("🔄 Refresh Chat"):
        st.rerun()

    # 2. Input box for new messages
    new_message = st.chat_input("Type your secret message here...")
    if new_message:
        # Encrypt the message and save it to the file
        encrypted_data = engine.encrypt(new_message)
        save_message(st.session_state.username, encrypted_data)
        st.rerun() # Refresh the page so the new message appears