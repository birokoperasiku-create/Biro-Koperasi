import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- CONFIG & LINK GOOGLE SHEETS ANDA ---
# Link ini sudah diubah dari format HTML ke format CSV agar bisa dibaca Python
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0yN69J6fYV0xDUKC919aVKP5WuN7d0A7GZn0QsIQzdG_MFGBRcnae4DjogoUIOW4ioJ1HdqPQHtO4/pub?output=csv"

st.set_page_config(page_title="Dashboard Keuangan Koperasi", layout="wide")


# --- FUNGSI AMBIL DATA ---
@st.cache_data(ttl=600)  # Data disimpan di cache selama 10 menit
def load_data():
    try:
        df_cloud = pd.read_csv(SHEET_URL)
        # Konversi kolom Tanggal (pastikan di Excel kolomnya bernama 'Tanggal')
        if 'Tanggal' in df_cloud.columns:
            df_cloud['Tanggal'] = pd.to_datetime(df_cloud['Tanggal'])
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
        st.write("Data bersumber dari Google Sheets yang Anda lampirkan.")

        # Menghitung Metrik
        # Pastikan nama kolom di Excel Anda pas: 'Masuk' dan 'Keluar'
        total_masuk = df["Masuk"].sum() if "Masuk" in df.columns else 0
        total_keluar = df["Keluar"].sum() if "Keluar" in df.columns else 0
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
            if "Tanggal" in df.columns:
                df_plot = df.sort_values("Tanggal").copy()
                df_plot["Saldo Kumulatif"] = (df_plot["Masuk"] - df_plot["Keluar"]).cumsum()
                fig = px.area(df_plot, x="Tanggal", y="Saldo Kumulatif", title="Trend Kas")
                st.plotly_chart(fig, use_container_width=True)

        with col_right:
            st.subheader("📝 Detail Transaksi")
            st.dataframe(df, use_container_width=True)
    else:
        st.warning(
            "Data tidak ditemukan. Pastikan kolom di Google Sheets memiliki judul: Tanggal, Kategori, Keterangan, Masuk, Keluar.")