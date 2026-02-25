import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# --- CONFIG & LINK GOOGLE SHEETS ---
# Link CSV untuk Dashboard (Public)
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0yN69J6fYV0xDUKC919aVKP5WuN7d0A7GZn0QsIQzdG_MFGBRcnae4DjogoUIOW4ioJ1HdqPQHtO4/pub?output=csv"
# Link UTAMA untuk Koneksi (Harus link yang bisa diedit)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1yN69J6fYV0xDUKC919aVKP5WuN7d0A7GZn0QsIQzdG_M/edit#gid=0"

st.set_page_config(page_title="Dashboard Keuangan Koperasi", layout="wide")

# --- CSS UNTUK LATAR BELAKANG HITAM & TEMA GELAP ---
st.markdown("""
    <style>
    /* Latar belakang utama hitam */
    .stApp {
        background-color: #0E1117;
        color: #FFFFFF;
    }
    /* Kartu metrik dengan latar belakang abu-abu gelap */
    [data-testid="stMetric"] {
        background-color: #161B22;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        border: 1px solid #30363D;
    }
    /* Input teks dan area teks */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: #0D1117;
        color: white;
        border: 1px solid #30363D;
    }
    /* Tombol */
    .stButton>button {
        background-color: #238636;
        color: white;
        border-radius: 8px;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True) # Perbaikan: Gunakan unsafe_allow_html

# --- FUNGSI AMBIL DATA ---
@st.cache_data(ttl=600)
def load_data():
    try:
        df_cloud = pd.read_csv(CSV_URL)
        if 'Tanggal' in df_cloud.columns:
            df_cloud['Tanggal'] = pd.to_datetime(df_cloud['Tanggal'])
        return df_cloud
    except Exception as e:
        return pd.DataFrame()

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
        pesan = st.text_area("Tulis saran di sini (identitas Anda tetap rahasia)...", height=150)
        
        if st.button("Kirim Saran"):
            if pesan:
                try:
                    # Inisialisasi koneksi
                    conn = st.connection("gsheets", type=GSheetsConnection)
                    
                    # Ambil data lama dari tab bernama 'Saran'
                    # Penting: Pastikan tab di Google Sheets Anda bernama 'Saran'
                    df_lama = conn.read(spreadsheet=SHEET_URL, worksheet="Saran", ttl=0)
                    
                    # Tambah baris baru
                    df_baru = pd.DataFrame([{"Tanggal": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Saran": pesan}])
                    df_final = pd.concat([df_lama, df_baru], ignore_index=True)
                    
                    # Update kembali ke Sheets
                    conn.update(spreadsheet=SHEET_URL, worksheet="Saran", data=df_final)
                    st.success("Saran berhasil terkirim!")
                    st.balloons()
                except Exception as e:
                    st.error(f"Gagal mengirim. Pastikan tab di Excel Anda bernama 'Saran' (case sensitive).")
                    st.info(f"Detail Error: {e}")
            else:
                st.warning("Mohon tuliskan pesan.")

# --- TAMPILAN DASHBOARD ---
else:
    st.sidebar.title("Menu Utama")
    if st.sidebar.button("🚪 Log Out"):
        st.session_state.logged_in = False
        st.rerun()

    df = load_data()

    if not df.empty:
        st.title("📊 Laporan Keuangan Real-Time")
        
        # Metrik
        total_masuk = pd.to_numeric(df["Masuk"], errors='coerce').sum() if "Masuk" in df.columns else 0
        total_keluar = pd.to_numeric(df["Keluar"], errors='coerce').sum() if "Keluar" in df.columns else 0
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Pemasukan", f"Rp {total_masuk:,.0f}")
        m2.metric("Pengeluaran", f"Rp {total_keluar:,.0f}")
        m3.metric("Saldo", f"Rp {total_masuk - total_keluar:,.0f}")

        st.markdown("---")
        
        # Grafik
        if "Tanggal" in df.columns:
            df_plot = df.sort_values("Tanggal").copy()
            df_plot["Saldo"] = (df_plot["Masuk"] - df_plot["Keluar"]).cumsum()
            fig = px.area(df_plot, x="Tanggal", y="Saldo", title="Trend Keuangan", template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("📋 Detail Transaksi")
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("Data tidak ditemukan atau kolom tidak sesuai.")
