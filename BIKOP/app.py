import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_gsheets import GSheetsConnection

# --- CONFIG & LINK GOOGLE SHEETS ---
# Pastikan di Google Sheets Anda minimal ada tab bernama 'Transaksi'
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
        st.error(f"Gagal memuat data dari tab '{worksheet_name}'. Pastikan nama tab sesuai.")
        return pd.DataFrame()

# --- SESSION STATE ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- LOGIKA HALAMAN ---
if not st.session_state.logged_in:
    # --- HALAMAN LOGIN ---
    st.title("☀️ Sistem Informasi Koperasi")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.subheader("🔑 Login Admin")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Masuk"):
            if u == "admin" and p == "koperasi123":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Username atau Password salah.")
else:
    # --- HALAMAN DASHBOARD ---
    st.sidebar.title("Menu")
    if st.sidebar.button("🚪 Keluar"):
        st.session_state.logged_in = False
        st.rerun()

    st.title("📊 Dashboard Keuangan")
    
    # Ambil data dari tab 'Transaksi' saja
    df = load_data("Transaksi")

    if not df.empty:
        # Pastikan kolom angka valid
        df['Masuk'] = pd.to_numeric(df['Masuk'], errors='coerce').fillna(0)
        df['Keluar'] = pd.to_numeric(df['Keluar'], errors='coerce').fillna(0)
        
        # Ringkasan Angka
        total_masuk = df['Masuk'].sum()
        total_keluar = df['Keluar'].sum()
        saldo = total_masuk - total_keluar
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Pemasukan", f"Rp {total_masuk:,.0f}")
        m2.metric("Pengeluaran", f"Rp {total_keluar:,.0f}")
        m3.metric("Saldo Akhir", f"Rp {saldo:,.0f}")

        st.divider()

        # Grafik (Jika ada kolom Tanggal)
        if 'Tanggal' in df.columns:
            df['Tanggal'] = pd.to_datetime(df['Tanggal'])
            df_plot = df.sort_values("Tanggal")
            df_plot["Saldo"] = (df_plot["Masuk"] - df_plot["Keluar"]).cumsum()
            fig = px.area(df_plot, x="Tanggal", y="Saldo", title="Tren Saldo", template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)

        # Tabel Data
        st.subheader("📋 Detail Transaksi Terakhir")
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("Data tidak tersedia. Harap periksa tab 'Transaksi' di Google Sheets Anda.")
