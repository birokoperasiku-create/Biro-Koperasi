import streamlit as st
import pandas as pd
import plotly.express as px

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Koperasi Digital", layout="wide", initial_sidebar_state="expanded")

# Custom CSS untuk tema cerah & bersih
# Custom CSS untuk tema cerah & bersih (Menggunakan unsafe_allow_html)
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    [data-testid="stMetric"] { 
        background-color: #ffffff; 
        padding: 20px; 
        border-radius: 10px; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.05); 
    }
    div.stButton > button:first-child { 
        background-color: #007bff; 
        color: white; 
        border-radius: 5px; 
    }
    </style>
    """, unsafe_allow_html=True)
# --- LINK INTEGRASI ---
# Ganti dengan link "Spreadsheet" Anda (Bukan link Publish to Web)
# Pastikan aksesnya "Anyone with the link can Edit"
SHEET_EDIT_URL = "https://docs.google.com/spreadsheets/d/1yN69J6fYV0xDUKC919aVKP5WuN7d0A7GZn0QsIQzdG_M/edit" 
# Link CSV untuk Grafik (Publish to Web -> CSV)
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0yN69J6fYV0xDUKC919aVKP5WuN7d0A7GZn0QsIQzdG_MFGBRcnae4DjogoUIOW4ioJ1HdqPQHtO4/pub?output=csv"

# --- FUNGSI AMBIL DATA ---
@st.cache_data(ttl=60)
def load_data():
    try:
        df = pd.read_csv(SHEET_CSV_URL)
        if 'Tanggal' in df.columns:
            df['Tanggal'] = pd.to_datetime(df['Tanggal'])
        return df
    except:
        return pd.DataFrame()

# --- SISTEM NAVIGASI ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("☀️ Selamat Datang di Biro Koperasi")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🔑 Login Admin")
        user = st.text_input("Username", placeholder="Masukkan username")
        pw = st.text_input("Password", type="password", placeholder="Masukkan password")
        if st.button("Masuk Sistem"):
            if user == "admin" and pw == "koperasi123":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Akun tidak ditemukan atau password salah.")
    
    with col2:
        st.subheader("🕵️ Kotak Saran Anonim")
        st.write("Suara Anda sangat berharga bagi kami. Identitas Anda akan tetap rahasia.")
        
        # Input Saran
        saran_anonim = st.text_area("Tulis saran, kritik, atau aspirasi Anda di sini:", height=150)
        
        if st.button("Kirim Saran Secara Anonim"):
            if saran_anonim.strip() == "":
                st.warning("Mohon isi saran sebelum mengirim.")
            else:
                # Simulasi pengiriman (Anda bisa menghubungkan ini ke Google Form API/Webhook nanti)
                st.success("✅ Terima kasih! Saran Anda telah terkirim secara anonim.")
                st.balloons() # Efek perayaan kecil

else:
    # --- DASHBOARD UTAMA ---
    st.sidebar.title("☀️ Navigasi")
    menu = st.sidebar.radio("Pilih Menu:", ["🏠 Dashboard Visual", "📝 Edit Data Excel", "📈 Analisis Trend"])
    
    if st.sidebar.button("🚪 Keluar"):
        st.session_state.logged_in = False
        st.rerun()

    df = load_data()

    if menu == "🏠 Dashboard Visual":
        st.title("📊 Ringkasan Keuangan")
        
        if not df.empty:
            t_masuk = df["Masuk"].sum() if "Masuk" in df.columns else 0
            t_keluar = df["Keluar"].sum() if "Keluar" in df.columns else 0
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Pemasukan", f"Rp {t_masuk:,.0f}", delta_color="normal")
            c2.metric("Pengeluaran", f"Rp {t_keluar:,.0f}", delta_color="inverse")
            c3.metric("Saldo Kas", f"Rp {t_masuk - t_keluar:,.0f}")
            
            st.subheader("Data Transaksi Terkini")
            st.dataframe(df.tail(10), use_container_width=True)
        else:
            st.info("Belum ada data untuk ditampilkan.")

    elif menu == "📝 Edit Data Excel":
        st.title("📝 Edit Spreadsheet Langsung")
        st.info("Perubahan di sini akan langsung tersimpan ke Google Sheets dan sinkron ke semua perangkat.")
        
        # Menggunakan IFrame untuk menampilkan Excel asli yang bisa diedit
        # Ganti '/edit' menjadi '/edit?rm=minimal' agar tampilan lebih bersih
        embed_url = SHEET_EDIT_URL.replace("/edit", "/edit?rm=minimal")
        st.components.v1.iframe(embed_url, height=600, scrolling=True)

    elif menu == "📈 Analisis Trend":
        st.title("📈 Analisis Grafik")
        if not df.empty and "Tanggal" in df.columns:
            df_plot = df.sort_values("Tanggal")
            df_plot["Saldo"] = (df_plot["Masuk"] - df_plot["Keluar"]).cumsum()
            fig = px.line(df_plot, x="Tanggal", y="Saldo", title="Pergerakan Saldo Kumulatif")
            st.plotly_chart(fig, use_container_width=True)


