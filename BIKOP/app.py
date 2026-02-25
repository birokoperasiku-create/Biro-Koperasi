import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# --- CONFIG & LINK GOOGLE SHEETS ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1yN69J6fYV0xDUKC919aVKP5WuN7d0A7GZn0QsIQzdG_M/edit#gid=0"

st.set_page_config(page_title="Dashboard Keuangan Koperasi", layout="wide")

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
def load_data(worksheet_name):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(spreadsheet=SHEET_URL, worksheet=worksheet_name, ttl=0)
        return df
    except Exception as e:
        return pd.DataFrame()

# --- SESSION STATE ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- LOGIKA HALAMAN ---
if not st.session_state.logged_in:
    # --- HALAMAN DEPAN (LOGIN & SARAN) ---
    st.title("☀️ Layanan Mandiri Koperasi")
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.subheader("🔑 Akses Admin")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Masuk Ke Sistem"):
            if u == "admin" and p == "koperasi123":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Kredensial salah.")

    with col2:
        st.subheader("🕵️ Kotak Saran & Laporan")
        st.write("Kirim masukan ke: birokoperasiku@gmail.com")
        
        pesan = st.text_area("Tulis saran di sini...", height=150)
        
        if st.button("Kirim Sekarang"):
            if pesan:
                try:
                    conn = st.connection("gsheets", type=GSheetsConnection)
                    df_saran = load_data("Saran")
                    
                    new_entry = pd.DataFrame([{
                        "Tanggal": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Isi Saran": pesan,
                        "Status": "Perlu Dicek"
                    }])
                    
                    df_final = pd.concat([df_saran, new_entry], ignore_index=True)
                    conn.update(spreadsheet=SHEET_URL, worksheet="Saran", data=df_final)
                    
                    st.success("✅ Terkirim ke Google Sheets!")
                    st.balloons()
                except Exception as e:
                    st.error(f"Gagal: Pastikan tab bernama 'Saran'
