import streamlit as st
import sqlite3
import pandas as pd
from docx import Document
import io
from datetime import datetime

# --- MA'LUMOTLAR BAZASI BILAN ISHLASH ---
def create_db():
    conn = sqlite3.connect('ustoz_pro.db')
    c = conn.cursor()
    # O'quvchilar jadvali
    c.execute('''CREATE TABLE IF NOT EXISTS students 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, grade TEXT)''')
    # Baholar jadvali
    c.execute('''CREATE TABLE IF NOT EXISTS marks 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER, 
                  subject TEXT, mark INTEGER, date TEXT)''')
    conn.commit()
    conn.close()

def add_student(name, grade):
    conn = sqlite3.connect('ustoz_pro.db')
    c = conn.cursor()
    c.execute("INSERT INTO students (name, grade) VALUES (?, ?)", (name, grade))
    conn.commit()
    conn.close()

# --- KONSEPT GENERATOR (Serverda saqlamaydi) ---
def create_docx(mavzu, matn):
    doc = Document()
    doc.add_heading('Ustoz Pro | Dars Konspekti', 0)
    doc.add_paragraph(f"Sana: {datetime.now().strftime('%Y-%m-%d')}")
    doc.add_paragraph(f"Mavzu: {mavzu}")
    doc.add_heading('Darsning borishi:', level=1)
    doc.add_paragraph(matn)
    
    # Faylni xotirada (RAM) saqlash
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- INTERFEYS ---
create_db()
st.set_page_config(page_title="Ustoz Pro", layout="wide")

st.sidebar.title("Ustoz Pro Menyu")
page = st.sidebar.radio("Bo'limni tanlang:", ["Jadval va Davomat", "O'quvchi qo'shish", "Konspekt Generator"])

# 1. JADVAL VA BAHOLASH
if page == "Jadval va Davomat":
    st.header("📝 Dars jarayoni va Baholash")
    conn = sqlite3.connect('ustoz_pro.db')
    students = pd.read_sql_query("SELECT * FROM students", conn)
    conn.close()

    if not students.empty:
        selected_student = st.selectbox("O'quvchini tanlang:", students['name'])
        baho = st.slider("Baho qo'ying:", 1, 5, 5)
        fan = st.text_input("Fan nomi:", "Fizika")
        
        if st.button("Bahoni saqlash va Ota-onaga yuborish (Simulatsiya)"):
            st.success(f"{selected_student}ga {fan} fanidan {baho} baho qo'yildi!")
            st.info("Telegram Bot orqali ota-onaga xabar ketdi (kod ulansa).")
    else:
        st.warning("Avval o'quvchi qo'shing!")

# 2. O'QUVCHI QO'SHISH
elif page == "O'quvchi qo'shish":
    st.header("🆕 Yangi o'quvchi ro'yxatga olish")
    ism = st.text_input("O'quvchi F.I.Sh:")
    sinf = st.text_input("Sinf (masalan: 9-A):")
    if st.button("Bazaga qo'shish"):
        add_student(ism, sinf)
        st.balloons()
        st.success("O'quvchi muvaffaqiyatli qo'shildi!")

# 3. KONSEPT GENERATOR
elif page == "Konspekt Generator":
    st.header("🤖 AI Konspekt Yaratuvchi")
    mavzu = st.text_input("Mavzuni kiriting:", "Arximed qonuni")
    
    # AI o'rniga hozircha universal shablon
    ai_matn = f"""{mavzu} mavzusi bo'yicha dars rejasi. 
    1. Mavzuning mohiyati va qonuniyatlari.
    2. Mavzuga doir misollar va masalalar yechish.
    3. O'quvchilarni baholash."""
    
    if st.button("Konspektni tayyorlash"):
        docx_file = create_docx(mavzu, ai_matn)
        st.download_button(
            label="📄 Word faylni yuklab olish",
            data=docx_file,
            file_name=f"{mavzu}_konspekt.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
