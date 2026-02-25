import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- CONFIG & LINK GOOGLE SHEETS TERBARU ---
# Link ini sudah diformat agar langsung mengunduh CSV dari Google Sheets yang Anda berikan
SHEET_ID = "1tgX-mcdxOdcFwtQdAexjFuniDoF4SLoEyWNQrqmH7o4"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

st.set_page_config(page_title="Dashboard Keuangan Koperasi", layout="wide")

# --- FUNGSI AMBIL DATA ---
@st.cache_data(ttl=600)  # Data disimpan di cache selama 10 menit
def load_data():
    try:
        # Membaca data dari link CSV
        df_cloud = pd.read_csv(SHEET_URL)
        
        # Konversi kolom Tanggal
        if 'Tanggal' in df_cloud.columns:
            df_cloud['Tanggal'] = pd.to_datetime(df_cloud['Tanggal'], errors='coerce')
        
        # Pastikan kolom angka tidak ada yang NaN/null agar perhitungan tidak error
        df_cloud['Masuk'] = df_cloud.get('Masuk', 0).fillna(0)
        df_cloud['Keluar'] = df_cloud.get('Keluar', 0).fillna(0)
        
        return df_cloud
    except Exception as e:
        st.error(f"Gagal memuat data: {e}")
        return pd.DataFrame()

# --- SISTEM LOGIN ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

def login():
    st.title("🔐 Login Biro Koperasi")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Masuk"):
        if username == "admin" and password == "koperasi123":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Akses Ditolak!")

# --- LOGIKA TAMPILAN ---
if not st.session_state.logged_in:
    login()
else:
    # Sidebar
    st.sidebar.title("Menu")
    if st.sidebar.button("🔄 Perbarui Data"):
        st.cache_data.clear()
        st.rerun()

    if st.sidebar.button("🚪 Log Out"):
        st.session_state.logged_in = False
        st.rerun()

    # Memuat Data
    df = load_data()

    if not df.empty:
        st.title("📊 Laporan Keuangan Real-Time")
        st.write(f"Menampilkan data dari link Google Sheets terbaru.")

        # Menghitung Metrik
        total_masuk = df["Masuk"].sum()
        total_keluar = df["Keluar"].sum()
        saldo = total_masuk - total_keluar

        m1, m2, m3 = st.columns(3)
        m1.metric("Total Pemasukan", f"Rp {total_masuk:,.0f}")
        m2.metric("Total Pengeluaran", f"Rp {total_keluar:,.0f}")
        m3.metric("Saldo Kas", f"Rp {saldo:,.0f}")

        st.markdown("---")

        # Visualisasi & Tabel
        col_left, col_right = st.columns([1, 1])

        with col_left:
            st.subheader("📈 Grafik Saldo")
            if "Tanggal" in df.columns and not df['Tanggal'].isnull().all():
                df_plot = df.dropna(subset=['Tanggal']).sort_values("Tanggal").copy()
                df_plot["Saldo Kumulatif"] = (df_plot["Masuk"] - df_plot["Kel
