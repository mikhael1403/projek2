import streamlit as st
import pandas as pd
import sqlite3

# --- KONFIGURASI DATABASE ---
def init_db():
    conn = sqlite3.connect('data_nilai.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS nilai_mahasiswa 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, nama TEXT, nilai INTEGER)''')
    conn.commit()
    return conn

conn = init_db()

# --- FUNGSI CRUD ---
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

# --- UI STREAMLIT ---
st.title("🚀 Sistem Input Nilai Mahasiswa")

# Sidebar untuk Login Admin
st.sidebar.title("Area Admin")
admin_password = st.sidebar.text_input("Password Admin", type="password")
is_admin = admin_password == "admin123" # Ganti password di sini

if is_admin:
    st.sidebar.success("Login Admin Berhasil")
else:
    if admin_password:
        st.sidebar.error("Password Salah")

# --- KONTEN UTAMA ---
tabs = st.tabs(["📝 Input Data", "📊 Lihat Nilai", "⚙️ Kelola (Admin)"])

# TAB 1: INPUT DATA (Untuk Siapa Saja)
with tabs[0]:
    st.header("Form Input Nilai")
    with st.form("form_input", clear_on_submit=True):
        nama_input = st.text_input("Nama Lengkap")
        nilai_input = st.number_input("Nilai", min_value=0, max_value=100)
        submit_btn = st.form_submit_button("Kirim Nilai")
        
        if submit_btn:
            if nama_input:
                add_data(nama_input, nilai_input)
                st.success(f"Data {nama_input} berhasil dikirim!")
            else:
                st.warning("Nama tidak boleh kosong")

# TAB 2: LIHAT DATA (Read-Only)
with tabs[1]:
    st.header("Daftar Nilai Saat Ini")
    df = get_all_data()
    if not df.empty:
        # Menampilkan data tanpa kolom ID agar lebih rapi untuk user biasa
        st.table(df[['nama', 'nilai']])
    else:
        st.info("Belum ada data.")

# TAB 3: ADMIN PANEL (CRUD)
with tabs[2]:
    if is_admin:
        st.header("Panel Kontrol Admin")
        df_admin = get_all_data()
        
        if not df_admin.empty:
            # Edit & Hapus Data
            selected_id = st.selectbox("Pilih ID Data untuk Edit/Hapus", df_admin['id'])
            selected_row = df_admin[df_admin['id'] == selected_id].iloc[0]
            
            col1, col2 = st.columns(2)
            with col1:
                new_nama = st.text_input("Edit Nama", value=selected_row['nama'])
                new_nilai = st.number_input("Edit Nilai", value=int(selected_row['nilai']))
                if st.button("Simpan Perubahan"):
                    update_data(selected_id, new_nama, new_nilai)
                    st.success("Data diperbarui!")
                    st.rerun()
            
            with col2:
                st.warning("Tindakan Berbahaya")
                if st.button("Hapus Data"):
                    delete_data(selected_id)
                    st.error("Data dihapus!")
                    st.rerun()
            
            st.divider()
            st.write("Preview Data Full (dengan ID):")
            st.dataframe(df_admin)
        else:
            st.info("Tidak ada data untuk dikelola.")
    else:
        st.error("Silakan masukkan password admin di sidebar untuk mengakses fitur ini.")
