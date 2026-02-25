import streamlit as st
import pandas as pd
import requests
import json

# --- KONFIGURASI ---
# GANTI INI dengan URL Web App dari langkah 1
WEB_APP_URL = "URL_APPS_SCRIPT_DISINI" 
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQww8g5_pyMq672ZX2vOm68_xCZvcCfTZNx4MEpURB-oJYo4YnxppaKnW6tGKomC0oyO2PMpIfK10XJ/pub?output=csv"

st.set_page_config(page_title="Koperasi Digital", layout="wide")

# CSS Tema Cerah & Bersih
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    [data-testid="stMetric"] { background-color: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; background-color: #007bff; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- TAMPILAN DEPAN ---
if not st.session_state.logged_in:
    st.title("☀️ Layanan Mandiri Koperasi")
    c1, c2 = st.columns([1, 1], gap="large")

    with c1:
        st.subheader("🔑 Akses Admin")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Masuk Ke Sistem"):
            if u == "admin" and p == "koperasi123":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Kredensial salah.")

    with c2:
        st.subheader("🕵️ Kotak Saran Anonim")
        pesan = st.text_area("Ada keluhan atau ide? Tulis di sini tanpa perlu identitas.", height=150)
        if st.button("Kirim Saran Sekarang"):
            if pesan.strip() != "":
                try:
                    # Proses pengiriman ke Google Sheets
                    response = requests.post(WEB_APP_URL, data=json.dumps({"saran": pesan}))
                    if response.status_code == 200:
                        st.success("Saran Anda telah terkirim ke sistem! Terima kasih.")
                        st.balloons()
                    else:
                        st.error("Terjadi kendala pada server penampung.")
                except:
                    st.error("Gagal mengirim. Periksa URL Apps Script Anda.")
            else:
                st.warning("Mohon tuliskan sesuatu sebelum mengirim.")

# --- TAMPILAN DASHBOARD ---
else:
    st.sidebar.title("☀️ Dashboard")
    if st.sidebar.button("Keluar (Logout)"):
        st.session_state.logged_in = False
        st.rerun()

    st.title("📊 Laporan Keuangan Real-Time")
    try:
        df = pd.read_csv(CSV_URL)
        # Metrik Sederhana
        col1, col2 = st.columns(2)
        if "Masuk" in df.columns and "Keluar" in df.columns:
            total_masuk = df["Masuk"].sum()
            total_keluar = df["Keluar"].sum()
            col1.metric("Total Pemasukan", f"Rp {total_masuk:,.0f}")
            col2.metric("Total Pengeluaran", f"Rp {total_keluar:,.0f}")
        
        st.markdown("---")
        st.subheader("Data Transaksi")
        st.dataframe(df, use_container_width=True)
    except:
        st.info("Sedang memuat data dari Google Sheets...")
