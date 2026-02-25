import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Data Keuangan Koperasi", layout="wide")

# --- LINK GOOGLE SHEETS ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1yN69J6fYV0xDUKC919aVKP5WuN7d0A7GZn0QsIQzdG_M/edit#gid=0"

# --- TAMPILAN GAYA (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    [data-testid="stMetric"] {
        background-color: #161B22;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #30363D;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Laporan Real-Time Google Sheets")

# --- FUNGSI AMBIL DATA ---
def load_all_data():
    try:
        # Menghubungkan ke Google Sheets
        conn = st.connection("gsheets", type=GSheetsConnection)
        # Membaca sheet utama/pertama secara langsung
        df = conn.read(spreadsheet=SHEET_URL, ttl=0)
        return df
    except Exception as e:
        st.error(f"Gagal memuat data. Pastikan link benar dan Spreadsheet dibagikan ke 'Anyone with the link'.")
        st.info(f"Detail Error: {e}")
        return pd.DataFrame()

# --- EKSEKUSI & TAMPILAN ---
df = load_all_data()

if not df.empty:
    # 1. Bagian Ringkasan Otomatis (Jika ada kolom Masuk & Keluar)
    cols = df.columns.tolist()
    masuk_col = next((c for c in cols if 'masuk' in c.lower()), None)
    keluar_col = next((c for c in cols if 'keluar' in c.lower()), None)

    if masuk_col and keluar_col:
        # Membersihkan data agar menjadi angka
        df[masuk_col] = pd.to_numeric(df[masuk_col], errors='coerce').fillna(0)
        df[keluar_col] = pd.to_numeric(df[keluar_col], errors='coerce').fillna(0)
        
        t_masuk = df[masuk_col].sum()
        t_keluar = df[keluar_col].sum()
        saldo = t_masuk - t_keluar

        m1, m2, m3 = st.columns(3)
        m1.metric("Total Pemasukan", f"Rp {t_masuk:,.0f}")
        m2.metric("Total Pengeluaran", f"Rp {t_keluar:,.0f}")
        m3.metric("Saldo Kas", f"Rp {saldo:,.0f}")
        
        st.divider()

    # 2. Tampilkan Tabel Seluruhnya
    st.subheader("📋 Data Tabel Lengkap")
    st.dataframe(df, use_container_width=True, height=600)
    
    # 3. Tombol Refresh
    if st.button("🔄 Perbarui Data"):
        st.cache_data.clear()
        st.rerun()

else:
    st.warning("Data tidak ditemukan atau sheet kosong.")
