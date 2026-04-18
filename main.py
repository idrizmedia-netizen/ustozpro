import streamlit as st
import sqlite3
import pandas as pd
from docx import Document
import io
from datetime import datetime

# --- 1. MA'LUMOTLAR BAZASI FUNKSIYALARI ---
def create_db():
    conn = sqlite3.connect('ustoz_pro.db', check_same_thread=False)
    c = conn.cursor()
    # O'quvchilar jadvali
    c.execute('''CREATE TABLE IF NOT EXISTS students 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, grade TEXT)''')
    # Baholar jadvali
    c.execute('''CREATE TABLE IF NOT EXISTS marks 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER, 
                  mark TEXT, comment TEXT, date TEXT)''')
    conn.commit()
    return conn

conn = create_db()

# --- 2. KONSEPT GENERATOR FUNKSIYASI ---
def create_docx(mavzu):
    doc = Document()
    doc.add_heading('Ustoz Pro | Dars Konspekti', 0)
    doc.add_paragraph(f"Sana: {datetime.now().strftime('%Y-%m-%d')}")
    doc.add_paragraph(f"Mavzu: {mavzu}")
    
    doc.add_heading('1. Darsning maqsadi:', level=1)
    doc.add_paragraph(f"O'quvchilarga {mavzu} haqida tushuncha berish va amaliy ko'nikmalarni shakllantirish.")
    
    doc.add_heading('2. Yangi mavzu bayoni:', level=1)
    doc.add_paragraph(f"{mavzu} mavzusi fanning muhim qismlaridan biri bo'lib, u o'quvchilarda nazariy va amaliy bilimlarni oshirishga xizmat qiladi.")
    
    doc.add_heading('3. Mustahkamlash uchun savollar:', level=1)
    doc.add_paragraph("1. Mavzuning asosiy qonuni nima?\n2. Ushbu hodisani hayotda qayerda ko'rishimiz mumkin?\n3. Mavzu yuzasidan xulosa qiling.")
    
    doc.add_heading('4. Uyga vazifa:', level=1)
    doc.add_paragraph(f"Mavzuni takrorlash va {mavzu}ga doir topshiriqlarni bajarish.")

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- 3. GOOGLE AUTH (KIRISH QISMI) ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

def login_page():
    st.title("🚀 Ustoz Pro — Kirish")
    st.info("Tizimdan foydalanish uchun shaxsingizni tasdiqlang.")
    if st.button("🔴 Google orqali kirish"):
        st.session_state.logged_in = True
        st.session_state.user_name = "Normurodov I.B." 
        st.rerun()

if not st.session_state.logged_in:
    login_page()
    st.stop()

# --- 4. ASOSIY SAHIFA SOZLAMALARI ---
st.set_page_config(page_title="Ustoz Pro | Digital System", layout="wide")

# Tepada o'qituvchi ma'lumotlari
col_head1, col_head2 = st.columns([3, 1])
with col_head1:
    st.subheader(f"👨‍🏫 O'qituvchi: {st.session_state.user_name}")
with col_head2:
    if st.button("Tizimdan chiqish"):
        st.session_state.logged_in = False
        st.rerun()

st.divider()

# --- 5. SIDEBAR (MENYU) ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3426/3426653.png", width=80)
st.sidebar.title("Ustoz Pro Menyu")
page = st.sidebar.radio("Bo'limni tanlang:", ["Jurnal", "O'quvchi qo'shish", "Konspekt Generator"])

# --- 6. BO'LIMLAR ---

# A. JURNAL BO'LIMI
if page == "Jurnal":
    st.header("📖 Sinf Jurnali")
    
    students_df = pd.read_sql_query("SELECT * FROM students", conn)
    
    if not students_df.empty:
        sinflar = students_df['grade'].unique()
        tanlangan_sinf = st.selectbox("📂 Sinfni tanlang:", sinflar)
        
        st.markdown(f"#### {tanlangan_sinf} sinfi jurnali — {datetime.now().strftime('%d.%m.%Y')}")
        
        filtrlangan = students_df[students_df['grade'] == tanlangan_sinf]
        
        # eMaktab uslubidagi sarlavhalar
        h_col1, h_col2, h_col3, h_col4 = st.columns([3, 1, 3, 1])
        h_col1.write("**F.I.Sh**")
        h_col2.write("**Baho**")
        h_col3.write("**Izoh**")
        h_col4.write("**Amal**")
        st.divider()

        for index, row in filtrlangan.iterrows():
            c1, c2, c3, c4 = st.columns([3, 1, 3, 1])
            with c1:
                st.write(f"{index+1}. {row['name']}")
            with c2:
                st.selectbox("Baho", ["-", "5", "4", "3", "2"], key=f"m_{row['id']}", label_visibility="collapsed")
            with c3:
                st.text_input("Izoh", placeholder="Darsda faol...", key=f"c_{row['id']}", label_visibility="collapsed")
            with c4:
                if st.button("Saqlash", key=f"b_{row['id']}"):
                    st.toast(f"{row['name']} baholandi!", icon="✅")
    else:
        st.warning("O'quvchilar topilmadi. Avval o'quvchi qo'shing.")

# B. O'QUVCHI QO'SHISH BO'LIMI (Yakkalik va Excel)
elif page == "O'quvchi qo'shish":
    st.header("🆕 O'quvchilarni tizimga kiritish")
    
    tab1, tab2 = st.tabs(["Yakkalik qo'shish", "Excel/CSV orqali yuklash"])
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            ism = st.text_input("O'quvchi F.I.Sh:", key="single_name")
        with col2:
            sinf = st.text_input("Sinf (masalan: 9-A):", key="single_grade")
        
        if st.button("Bazaga saqlash", key="save_single"):
            if ism and sinf:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO students (name, grade) VALUES (?, ?)", (ism, sinf))
                conn.commit()
                st.success(f"{ism} muvaffaqiyatli qo'shildi!")
                st.balloons()
            else:
                st.error("Iltimos, ism va sinfni to'liq kiriting!")
    
    with tab2:
        st.subheader("📁 Fayl orqali ommaviy yuklash")
        st.info("Fayl ustunlari nomi 'name' va 'grade' bo'lishi kerak.")
        uploaded_file = st.file_uploader("Excel yoki CSV faylni tanlang", type=["xlsx", "csv"])
        
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                st.write("Fayl tarkibi (birinchi 5 qator):", df.head())
                
                if st.button("Barcha o'quvchilarni bazaga yuklash"):
                    cursor = conn.cursor()
                    for index, row in df.iterrows():
                        cursor.execute("INSERT INTO students (name, grade) VALUES (?, ?)", 
                                     (str(row['name']), str(row['grade'])))
                    conn.commit()
                    st.success(f"{len(df)} ta o'quvchi bazaga muvaffaqiyatli qo'shildi!")
                    st.balloons()
            except Exception as e:
                st.error(f"Xatolik: {e}. Ustunlar 'name' va 'grade' ekanini tekshiring.")

# C. KONSEPT GENERATOR BO'LIMI
elif page == "Konspekt Generator":
    st.header("🤖 AI Konspekt Generator")
    mavzu = st.text_input("Mavzu nomini kiriting:", "Fizik hodisalar")
    
    if st.button("To'liq konspekt yaratish"):
        file_data = create_docx(mavzu)
        st.success(f"'{mavzu}' mavzusi bo'yicha hujjat tayyorlandi!")
        st.download_button(
            label="📄 Word faylni yuklab olish",
            data=file_data,
            file_name=f"{mavzu}_konspekt.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
