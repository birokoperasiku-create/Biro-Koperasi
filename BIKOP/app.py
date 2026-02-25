import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# --- KONFIGURASI ---
# Link CSV untuk Dashboard (tetap pakai link pub)
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQww8g5_pyMq672ZX2vOm68_xCZvcCfTZNx4MEpURB-oJYo4YnxppaKnW6tGKomC0oyO2PMpIfK10XJ/pub?output=csv"
# Link EDIT untuk GSheets Connection (pastikan akses: Anyone with link can EDIT)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1yN69J6fYV0xDUKC919aVKP5WuN7d0A7GZn0QsIQzdG_M/edit#gid=0"

st.set_page_config(page_title="Koperasi Digital", layout="wide")

# CSS Perbaikan (Menghilangkan error unsafe_base_config)
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

# --- TAMPILAN DEPAN (LOGIN & SARAN) ---
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
        pesan = st.text_area("Tulis saran di sini (identitas Anda tetap rahasia)...")
        
        if st.button("Kirim Saran"):
            if pesan:
                try:
                    # Koneksi ke GSheets
                    conn = st.connection("gsheets", type=GSheetsConnection)
                    # Baca data lama dari sheet bernama "Saran"
                    df_lama = conn.read(spreadsheet=SHEET_URL, worksheet="Saran")
                    
                    # Tambah baris baru
                    df_baru = pd.DataFrame([{"Tanggal": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Saran": pesan}])
                    df_final = pd.concat([df_lama, df_baru], ignore_index=True)
                    
                    # Tulis balik ke Sheets
                    conn.update(spreadsheet=SHEET_URL, worksheet="Saran", data=df_final)
                    st.success("Saran berhasil terkirim secara anonim!")
                    st.balloons()
                except Exception as e:
                    st.error(f"Gagal mengirim. Pastikan tab bernama 'Saran' ada di Google Sheets. Error: {e}")
            else:
                st.warning("Mohon isi kotak saran.")

# --- TAMPILAN DASHBOARD (SETELAH LOGIN) ---
else:
    st.sidebar.title("☀️ Dashboard")
    if st.sidebar.button("Keluar (Logout)"):
        st.session_state.logged_in = False
        st.rerun()

    st.title("📊 Laporan Keuangan Real-Time")
    try:
        df = pd.read_csv(CSV_URL)
        
        # Hitung Metrik
        col_m1, col_m2 = st.columns(2)
        if "Masuk" in df.columns and "Keluar" in df.columns:
            total_masuk = pd.to_numeric(df["Masuk"], errors='coerce').sum()
            total_keluar = pd.to_numeric(df["Keluar"], errors='coerce').sum()
            col_m1.metric("Total Pemasukan", f"Rp {total_masuk:,.0f}")
            col_m2.metric("Total Pengeluaran", f"Rp {total_keluar:,.0f}")
        
        st.markdown("---")
        st.subheader("Data Transaksi Terkini")
        st.dataframe(df, use_container_width=True)
    except:
        st.info("Sedang memuat data...")
