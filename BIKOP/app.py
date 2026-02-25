import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# --- KONFIGURASI ---
# Link CSV untuk Dashboard (Public)
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQww8g5_pyMq672ZX2vOm68_xCZvcCfTZNx4MEpURB-oJYo4YnxppaKnW6tGKomC0oyO2PMpIfK10XJ/pub?output=csv"
# Link UTAMA untuk Koneksi (Harus link yang bisa diedit)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1yN69J6fYV0xDUKC919aVKP5WuN7d0A7GZn0QsIQzdG_M/edit#gid=0"

st.set_page_config(page_title="Koperasi Digital", layout="wide")

# Perbaikan CSS (Menghapus 'unsafe_base_config' yang bikin error di screenshot 1)
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
        pesan = st.text_area("Tulis saran di sini...", height=150)
        
        if st.button("Kirim Saran"):
            if pesan:
                try:
                    # Inisialisasi koneksi
                    conn = st.connection("gsheets", type=GSheetsConnection)
                    
                    # Baca data lama dari tab 'Saran'
                    # Jika tab tidak ditemukan, ini akan memicu error
                    df_lama = conn.read(spreadsheet=SHEET_URL, worksheet="Saran", ttl=0)
                    
                    # Buat data baru
                    df_baru = pd.DataFrame([{"Tanggal": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Saran": pesan}])
                    
                    # Gabungkan
                    df_final = pd.concat([df_lama, df_baru], ignore_index=True)
                    
                    # Update kembali ke Sheets
                    conn.update(spreadsheet=SHEET_URL, worksheet="Saran", data=df_final)
                    st.success("Saran berhasil terkirim!")
                    st.balloons()
                except Exception as e:
                    st.error(f"Gagal mengirim. Solusi: Pastikan tab di Excel Anda bernama 'Saran' (case sensitive).")
                    st.info(f"Detail Error: {e}")
            else:
                st.warning("Mohon tuliskan pesan.")

# --- TAMPILAN DASHBOARD ---
else:
    st.sidebar.title("☀️ Menu")
    if st.sidebar.button("Keluar (Logout)"):
        st.session_state.logged_in = False
        st.rerun()

    st.title("📊 Laporan Keuangan Real-Time")
    try:
        df_dash = pd.read_csv(CSV_URL)
        st.dataframe(df_dash, use_container_width=True)
    except:
        st.warning("Gagal memuat data dashboard.")
