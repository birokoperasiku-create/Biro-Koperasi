import streamlit as st
import pandas as pd
import requests
import json

# --- KONFIGURASI ---
# GANTI INI dengan URL Web App dari langkah 1
WEB_APP_URL = "URL_APPS_SCRIPT_DISINI" 
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQww8g5_pyMq672ZX2vOm68_xCZvcCfTZNx4MEpURB-oJYo4YnxppaKnW6tGKomC0oyO2PMpIfK10XJ/pub?output=csv"

st.set_page_config(page_title="Koperasi Digital", layout="wide")

# Perbaikan CSS agar tidak error
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    [data-testid="stMetric"] { 
        background-color: white; 
        padding: 20px; 
        border-radius: 12px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); 
    }
    </style>
    """, unsafe_allow_html=True) # Gunakan unsafe_allow_html, bukan unsafe_base_config

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

   from streamlit_gsheets import GSheetsConnection

# 1. Buat koneksi (Ganti link dengan link Google Sheets Edit kamu)
url = "https://docs.google.com/spreadsheets/d/1yN69J6fYV0xDUKC919aVKP5WuN7d0A7GZn0QsIQzdG_M/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. Logika Kirim Saran
with col2:
    st.subheader("🕵️ Kotak Saran Anonim")
    pesan = st.text_area("Tulis saran di sini...")
    
    if st.button("Kirim"):
        if pesan:
            # Ambil data lama dari tab bernama "Saran"
            df_lama = conn.read(spreadsheet=url, worksheet="Saran")
            
            # Tambahkan baris baru
            df_baru = pd.DataFrame([{"Tanggal": datetime.now(), "Saran": pesan}])
            df_final = pd.concat([df_lama, df_baru], ignore_index=True)
            
            # Update kembali ke Google Sheets
            conn.update(spreadsheet=url, worksheet="Saran", data=df_final)
            st.success("Saran berhasil masuk ke Sheet!")

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

