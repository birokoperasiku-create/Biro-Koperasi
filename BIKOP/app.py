import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import json

# --- CONFIG ---
st.set_page_config(page_title="Koperasi Digital", layout="wide")

# Masukkan URL dari Web App Deployment Anda di sini
WEB_APP_URL = "ISI_DENGAN_URL_APPS_SCRIPT_ANDA" 
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQww8g5_pyMq672ZX2vOm68_xCZvcCfTZNx4MEpURB-oJYo4YnxppaKnW6tGKomC0oyO2PMpIfK10XJ/pub?output=csv"
SHEET_EDIT_URL = "https://docs.google.com/spreadsheets/d/1yN69J6fYV0xDUKC919aVKP5WuN7d0A7GZn0QsIQzdG_M/edit"

# CSS Tema Cerah
st.markdown("""
    <style>
    .stApp { background-color: #f0f2f6; }
    [data-testid="stMetric"] { background-color: white; border-radius: 10px; padding: 15px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- HALAMAN DEPAN (LOGIN & SARAN) ---
if not st.session_state.logged_in:
    st.title("☀️ Sistem Informasi Koperasi")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🔑 Login Admin")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Masuk"):
            if u == "admin" and p == "koperasi123":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Gagal Login")

    with col2:
        st.subheader("🕵️ Kotak Saran Anonim")
        saran_input = st.text_area("Apa masukan Anda untuk kami?", placeholder="Tulis di sini...")
        if st.button("Kirim Saran"):
            if saran_input:
                try:
                    # Mengirim data ke Google Sheets via Apps Script
                    requests.post(WEB_APP_URL, data=json.dumps({"saran": saran_input}))
                    st.success("Saran terkirim secara anonim! Terima kasih.")
                    st.balloons()
                except:
                    st.error("Gagal terhubung ke server.")
            else:
                st.warning("Isi saran dulu ya.")

# --- HALAMAN DASHBOARD (SETELAH LOGIN) ---
else:
    st.sidebar.title("Menu Utama")
    nav = st.sidebar.radio("Pilih:", ["Dashboard", "Edit Data Excel"])
    
    if st.sidebar.button("Log Out"):
        st.session_state.logged_in = False
        st.rerun()

    if nav == "Dashboard":
        st.title("📊 Laporan Real-Time")
        df = pd.read_csv(SHEET_CSV_URL)
        # (Tambahkan logika metrik dan grafik seperti sebelumnya di sini)
        st.dataframe(df, use_container_width=True)

    elif nav == "Edit Data Excel":
        st.title("📝 Edit Spreadsheet")
        embed_url = SHEET_EDIT_URL.replace("/edit", "/edit?rm=minimal")
        st.components.v1.iframe(embed_url, height=700)
