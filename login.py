import streamlit as st
import pandas as pd
import os

USER_FILE = "users.csv"

if not os.path.exists(USER_FILE):
    pd.DataFrame(columns=["username", "password"]).to_csv(USER_FILE, index=False)


# ================= STYLE =================
def apply_style():
    st.markdown("""
    <style>

    .stApp {
        background: linear-gradient(135deg, #020617, #0f172a);
    }

    /* REMOVE FULL HEIGHT CENTERING */
    .main-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        margin-top: 60px;
    }

    /* TITLE */
    .title {
        font-size: 32px;
        font-weight: 800;
        color: white;
        text-align: center;
        margin-bottom: 20px;
    }

    .highlight {
        color: #22c55e;
    }

    /* CARD */
    .card {
        width: 360px;
        background: rgba(2,6,23,0.9);
        padding: 25px;
        border-radius: 12px;
        border: 1px solid #334155;
        box-shadow: 0 20px 60px rgba(0,0,0,0.6);
    }

    /* BUTTON */
    .stButton button {
        background-color: #22c55e;
        color: black;
        height: 40px;
        font-weight: 600;
    }

    </style>
    """, unsafe_allow_html=True)


# ================= LOGIN =================
def login_page():

    apply_style()

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    # STATE
    if "page" not in st.session_state:
        st.session_state.page = "Login"

    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    # TITLE (TOP CENTER)
    st.markdown("""
    <div class="title">
        AI BASED <span class="highlight">STOCK MARKET</span><br>
        FORECASTING SYSTEM
    </div>
    """, unsafe_allow_html=True)

    # CARD BELOW TITLE
    st.markdown('<div class="card">', unsafe_allow_html=True)

    # 🔥 RADIO BUTTON (KEPT AS YOU WANTED)
    option = st.radio("", ["Login", "Signup"], horizontal=True)

    df = pd.read_csv(USER_FILE)

    # LOGIN
    if option == "Login":
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login", use_container_width=True):
            if ((df['username'] == username) & (df['password'] == password)).any():
                st.session_state.logged_in = True
                st.session_state.user = username
                st.rerun()
            else:
                st.error("Invalid username or password")

        if st.button("Forgot Password"):
            st.session_state.page = "Reset"

    # SIGNUP
    else:
        new_user = st.text_input("Username")
        new_pass = st.text_input("Password", type="password")
        confirm_pass = st.text_input("Confirm Password", type="password")

        if st.button("Create Account", use_container_width=True):
            if new_user in df['username'].values:
                st.error("User already exists")
            elif new_pass != confirm_pass:
                st.error("Passwords do not match")
            else:
                new = pd.DataFrame([[new_user, new_pass]], columns=["username", "password"])
                df = pd.concat([df, new], ignore_index=True)
                df.to_csv(USER_FILE, index=False)
                st.success("Account created successfully")

    # RESET PASSWORD (separate flow)
    if st.session_state.page == "Reset":
        st.markdown("### Reset Password")

        user = st.text_input("Username")
        new_pass = st.text_input("New Password", type="password")
        confirm_pass = st.text_input("Confirm Password", type="password")

        if st.button("Reset Password"):
            if user not in df['username'].values:
                st.error("User not found")
            elif new_pass != confirm_pass:
                st.error("Passwords do not match")
            else:
                df.loc[df['username'] == user, 'password'] = new_pass
                df.to_csv(USER_FILE, index=False)
                st.success("Password updated")

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    return st.session_state.logged_in