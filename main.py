import streamlit as st
import sqlite3
import pandas as pd
from docx import Document
import io
from datetime import datetime

# --- MA'LUMOTLAR BAZASI ---
def create_db():
    conn = sqlite3.connect('ustoz_pro.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS students 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, grade TEXT)''')
    conn.commit()
    conn.close()

create_db()

# --- KONSEPT GENERATOR (Kengaytirilgan) ---
def create_docx(mavzu):
    doc = Document()
    doc.add_heading('Ustoz Pro | Dars Konspekti', 0)
    doc.add_paragraph(f"Sana: {datetime.now().strftime('%Y-%m-%d')}")
    doc.add_paragraph(f"Mavzu: {mavzu}")
    
    # Bu yerda AI o'rniga to'liqroq strukturani chiqaramiz
    doc.add_heading('1. Darsning maqsadi:', level=1)
    doc.add_paragraph(f"O'quvchilarga {mavzu} haqida tushuncha berish va amaliy ko'nikmalarni shakllantirish.")
    
    doc.add_heading('2. Yangi mavzu bayoni:', level=1)
    doc.add_paragraph(f"{mavzu} mavzusi fizika fanining muhim qismlaridan biri bo'lib, u tabiatdagi hodisalarni tushuntirishda xizmat qiladi...")
    
    doc.add_heading('3. Mustahkamlash uchun savollar:', level=1)
    doc.add_paragraph("1. Mavzuning asosiy qonuni nima?\n2. Ushbu hodisani hayotda qayerda ko'rishimiz mumkin?\n3. Masala yechish namunasi.")
    
    doc.add_heading('4. Uyga vazifa:', level=1)
    doc.add_paragraph(f"Mavzuni o'qish va {mavzu}ga doir 3 ta masala yechish.")

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- INTERFEYS ---
st.set_page_config(page_title="Ustoz Pro", layout="wide")
st.sidebar.title("Ustoz Pro Menyu")
page = st.sidebar.radio("Bo'limni tanlang:", ["Jadval va Baholash", "O'quvchi qo'shish", "Konspekt Generator"])

# 1. JADVAL VA BAHOLASH (Sinf bo'yicha filtrlash qo'shildi)
if page == "Jadval va Baholash":
    st.header("📝 Dars jarayoni va Baholash")
    
    conn = sqlite3.connect('ustoz_pro.db')
    students_df = pd.read_sql_query("SELECT * FROM students", conn)
    conn.close()

    if not students_df.empty:
        # 1. Avval sinfni tanlash
        sinflar = students_df['grade'].unique()
        tanlangan_sinf = st.selectbox("Sinfni tanlang:", sinflar)
        
        # 2. Tanlangan sinfdagi o'quvchilarni ajratib olish
        filtrlangan_uquvchilar = students_df[students_df['grade'] == tanlangan_sinf]
        
        # 3. Faqat o'sha sinf o'quvchilarini ko'rsatish
        tanlangan_ism = st.selectbox("O'quvchini tanlang:", filtrlangan_uquvchilar['name'])
        
        baho = st.slider("Baho qo'ying:", 1, 5, 5)
        fan = st.text_input("Fan nomi:", "Fizika")
        
        if st.button("Bahoni saqlash va Xabar yuborish"):
            st.success(f"{tanlangan_sinf} sinfi o'quvchisi {tanlangan_ism}ga {baho} qo'yildi!")
    else:
        st.warning("Hali o'quvchilar bazaga qo'shilmagan.")

# 2. O'QUVCHI QO'SHISH
elif page == "O'quvchi qo'shish":
    st.header("🆕 Yangi o'quvchi qo'shish")
    col1, col2 = st.columns(2)
    with col1:
        ism = st.text_input("F.I.Sh:")
    with col2:
        sinf = st.text_input("Sinf (masalan: 9-A):")
    
    if st.button("Bazaga saqlash"):
        if ism and sinf:
            conn = sqlite3.connect('ustoz_pro.db')
            c = conn.cursor()
            c.execute("INSERT INTO students (name, grade) VALUES (?, ?)", (ism, sinf))
            conn.commit()
            conn.close()
            st.success(f"{ism} muvaffaqiyatli qo'shildi!")
        else:
            st.error("Iltimos, barcha maydonlarni to'ldiring!")

# 3. KONSEPT GENERATOR
elif page == "Konspekt Generator":
    st.header("🤖 Konspekt Generator")
    mavzu = st.text_input("Mavzu nomini kiriting:", "Moddalar haqida")
    
    if st.button("Toliq konspekt yaratish"):
        file = create_docx(mavzu)
        st.download_button(
            label="📄 Word faylni yuklab olish",
            data=file,
            file_name=f"{mavzu}_konspekt.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
