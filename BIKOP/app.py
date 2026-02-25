import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Dashboard Koperasi BIKOP", layout="wide")

# --- LINK GOOGLE SHEETS ANDA ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1tgX-mcdxOdcFwtQdAexjFuniDoF4SLoEyWNQrqmH7o4/edit?usp=sharing"

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    [data-testid="stMetric"] {
        background-color: #161B22;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #30363D;
    }
    .stButton>button { width: 100%; background-color: #238636; color: white; border: none; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNGSI AMBIL DATA ---
def load_data():
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(spreadsheet=SHEET_URL, ttl=0)
        return df
    except Exception as e:
        st.error(f"Gagal memuat data: {e}")
        return pd.DataFrame()

# --- SISTEM LOGIN ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    # --- HALAMAN LOGIN ---
    st.title("☀️ Selamat Datang di BIKOP")
    c1, c2, c3 = st.columns([1, 2, 1])
    
    with c2:
        st.subheader("🔑 Login Admin")
        username = st.text_input("Username", key="user")
        password = st.text_input("Password", type="password", key="pass")
        
        if st.button("Masuk Ke Dashboard"):
            if username == "admin" and password == "koperasi123":
                st.session_state.logged_in = True
