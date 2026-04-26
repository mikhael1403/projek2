import streamlit as st
import pandas as pd
import sqlite3

# --- KONFIGURASI DATABASE ---
def init_db():
    conn = sqlite3.connect('data_nilai.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS nilai_mahasiswa 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, nama TEXT, nilai INTEGER)''')
    conn.commit()
    return conn

conn = init_db()

# --- FUNGSI LOGIKA ---
def add_data(nama, nilai):
    with conn:
        conn.execute('INSERT INTO nilai_mahasiswa(nama, nilai) VALUES (?,?)', (nama, nilai))

def delete_data(id_data):
    with conn:
        conn.execute('DELETE FROM nilai_mahasiswa WHERE id = ?', (id_data,))

def update_data(id_data, new_nama, new_nilai):
    with conn:
        conn.execute('UPDATE nilai_mahasiswa SET nama = ?, nilai = ? WHERE id = ?', (new_nama, new_nilai, id_data))

def get_all_data():
    return pd.read_sql('SELECT * FROM nilai_mahasiswa', conn)

def tentukan_grade(nilai):
    if nilai >= 90: return 'A'
    elif nilai >= 80: return 'B'
    elif nilai >= 70: return 'C'
    elif nilai >= 60: return 'D'
    else: return 'E'

# --- UI STREAMLIT ---
st.set_page_config(page_title="Input Nilai Informatika", layout="centered")
st.title("🚀 Sistem Input Nilai Mahasiswa")

# --- LOGIC LOGIN/LOGOUT ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

st.sidebar.title("🔐 Area Admin")

if not st.session_state['authenticated']:
    # Form Login
    admin_password = st.sidebar.text_input("Password Admin", type="password")
    if st.sidebar.button("Login"):
        if admin_password == "admin123": # <--- GANTI PASSWORD DI SINI
            st.session_state['authenticated'] = True
            st.rerun()
        else:
            st.sidebar.error("Password Salah")
else:
    # Tampilan kalau sudah login
    st.sidebar.success("Mode Admin Aktif")
    if st.sidebar.button("Logout"):
        st.session_state['authenticated'] = False
        st.rerun()

is_admin = st.session_state['authenticated']

# --- KONTEN UTAMA ---
tabs = st.tabs(["📝 Input Data", "📊 Lihat Nilai", "⚙️ Kelola (Admin)"])

# TAB 1: INPUT DATA
with tabs[0]:
    st.header("Form Input Nilai")
    with st.form("form_input", clear_on_submit=True):
        nama_input = st.text_input("Nama Lengkap")
        nilai_input = st.number_input("Nilai", min_value=0, max_value=100, step=1)
        submit_btn = st.form_submit_button("Kirim Nilai")
        
        if submit_btn:
            if nama_input.strip():
                add_data(nama_input, nilai_input)
                st.success(f"Data {nama_input} berhasil dikirim!")
            else:
                st.warning("Nama tidak boleh kosong")

# TAB 2: LIHAT DATA (Read-Only)
with tabs[1]:
    st.header("Daftar Nilai Saat Ini")
    df = get_all_data()
    if not df.empty:
        # Tambahkan Grade sebelum ditampilkan
        df['Grade'] = df['nilai'].apply(tentukan_grade)
        # Rapikan nama kolom untuk user
        df_display = df[['nama', 'nilai', 'Grade']].rename(columns={'nama': 'Nama', 'nilai': 'Nilai'})
        st.table(df_display)
    else:
        st.info("Belum ada data yang masuk.")

# TAB 3: ADMIN PANEL (CRUD)
with tabs[2]:
    if is_admin:
        st.header("Panel Kontrol Admin")
        df_admin = get_all_data()
        
        if not df_admin.empty:
            # Pilihan Edit/Hapus
            st.subheader("Edit atau Hapus Data")
            selected_id = st.selectbox("Pilih ID Data", df_admin['id'])
            selected_row = df_admin[df_admin['id'] == selected_id].iloc[0]
            
            col1, col2 = st.columns(2)
            with col1:
                new_nama = st.text_input("Edit Nama", value=selected_row['nama'])
                new_nilai = st.number_input("Edit Nilai", value=int(selected_row['nilai']), min_value=0, max_value=100)
                if st.button("💾 Simpan Perubahan"):
                    update_data(selected_id, new_nama, new_nilai)
                    st.success("Data diperbarui!")
                    st.rerun()
            
            with col2:
                st.write("---")
                if st.button("🗑️ Hapus Data"):
                    delete_data(selected_id)
                    st.error("Data dihapus!")
                    st.rerun()
            
            st.divider()
            st.subheader("Data Master (Database)")
            df_admin['Grade'] = df_admin['nilai'].apply(tentukan_grade)
            st.dataframe(df_admin)
        else:
            st.info("Database kosong.")
    else:
        st.warning("Gunakan sidebar untuk login sebagai Admin agar bisa mengelola data.")

# Footer
st.caption("Dibuat untuk tugas kuliah Mikha • Informatika 2026")
