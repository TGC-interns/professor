"""
import streamlit as st
import requests
import firebase_admin
from firebase_admin import credentials, firestore
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Firebase Admin once
if not firebase_admin._apps:
    # Reconstruct the credentials JSON from .env variables
    firebase_config = {
        "type": os.getenv("TYPE"),
        "project_id": os.getenv("PROJECT_ID"),
        "private_key_id": os.getenv("PRIVATE_KEY_ID"),
        "private_key": os.getenv("PRIVATE_KEY").replace("\\n", "\n"),
        "client_email": os.getenv("CLIENT_EMAIL"),
        "client_id": os.getenv("CLIENT_ID"),
        "auth_uri": os.getenv("AUTH_URI"),
        "token_uri": os.getenv("TOKEN_URI"),
        "auth_provider_x509_cert_url": os.getenv("AUTH_PROVIDER_X509_CERT_URL"),
        "client_x509_cert_url": os.getenv("CLIENT_X509_CERT_URL"),
        "universe_domain": os.getenv("UNIVERSE_DOMAIN"),
    }

    # Initialize Firebase with the loaded credentials
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Firebase API Key for authentication
API_KEY = st.secrets["firebase"]["apiKey"]

def firebase_sign_in(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    res = requests.post(url, json=payload)
    if res.status_code == 200:
        return res.json()
    return None

def get_role(uid):
    doc = db.collection("users").document(uid).get()
    if doc.exists:
        data = doc.to_dict()
        return data.get("role", "Teacher")
    return "Teacher"

def teacher_login():
    st.title("🔐 Teacher Login Portal")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = firebase_sign_in(email, password)
        if user:
            uid = user["localId"]
            role = get_role(uid)

            st.session_state.logged_in = True
            st.session_state.username = email
            st.session_state.role = role
            st.session_state.user = {
                "email": email,
                "uid": uid,
                "role": role
            }

            st.success(f"✅ Logged in as {role}: {email}")
            st.rerun()
        else:
            st.error("❌ Invalid email or password.")
"""