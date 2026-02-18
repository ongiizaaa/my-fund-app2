import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="AVP Fund Finder v2 (Debug Mode)", layout="wide")

# ฟังก์ชันโหลดข้อมูลแบบลดความเสี่ยง
@st.cache_data(show_spinner="กำลังโหลดข้อมูล...")
def load_data_safe():
    excel_file = 'fund_stat_web.xlsx'
    
    # รอบนี้เราจะข้าม Parquet ไปก่อนเพื่อเช็กความสดใหม่ของข้อมูล
    if os.path.exists(excel_file):
        try:
            df = pd.read_excel(excel_file, engine='openpyxl')
            df.columns = df.columns.str.strip()
            # แปลงค่าในคอลัมน์ตัวเลขให้ปลอดภัย (ถ้าไม่ใช่ตัวเลขให้เป็น 0)
            for col in ['TER', 'Front', 'Back']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            return df
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดในการอ่านไฟล์ Excel: {e}")
            return pd.DataFrame()
    else:
        st.error(f"ไม่พบไฟล์ {excel_file} ใน Folder เดียวกับโค้ด")
        return pd.DataFrame()

df = load_data_safe()

st.title("⚡ ค้นหาข้อมูลกองทุน by FP2")

# ลองพิมพ์ชื่อคอลัมน์ที่โหลดได้จริงออกมาดู
if not df.empty:
    st.info(f"✅ โหลดข้อมูลสำเร็จพบทั้งหมด {len(df)} แถว")
    
    query = st.text_input("🔍 พิมพ์ชื่อกองทุน:", placeholder="เช่น SCB, K-CASH...").strip()
    
    filtered = df[df['fund_name'].astype(str).str.contains(query, case=False, na=False)] if query else df.head(20)

    # หัวตาราง
    col_ratios = [2.2, 1.8, 0.7, 0.7, 0.7, 1.2, 1.0]
    h = st.columns(col_ratios)
    headers = ["ชื่อกองทุน", "ประเภทกองทุน (AVP Cate)", "รวมค่าใช้จ่าย (TER %)", "ค่าธรรมเนียมขาย (Front)", "ค่าธรรมเนียมรับซื้อคืน (Back)", "อัปเดตเมื่อ", "เอกสาร (Fund Fact Sheet)"]
    for col, text in zip(h, headers):
        col.write(f"**{text}**")
    st.divider()

    # แสดงผล
    for i, row in filtered.iterrows():
        try:
            c = st.columns(col_ratios)
            c[0].write(row.get('fund_name', 'N/A'))
            c[1].write(row.get('AVP Cate', '-'))
            c[2].write(f"{row.get('TER', 0):.2f}")
            c[3].write(f"{row.get('Front', 0):.2f}")
            c[4].write(f"{row.get('Back', 0):.2f}")
            c[5].write(str(row.get('as_of_date', '-')))
            
            # ลิงก์ PDF
            raw_pdf = str(row.get('pdf_factsheet', '#'))
            google_url = f"https://docs.google.com/viewer?url={raw_pdf}"
            
            btn = f'''<a href="{google_url}" target="_blank" style="text-decoration:none;">
                        <div style="background-color:#ff4b4b;color:white;padding:5px;border-radius:5px;text-align:center;font-size:13px;font-weight:bold;">📄 เปิด</div>
                      </a>'''
            c[6].markdown(btn, unsafe_allow_html=True)
        except Exception as e:
            # ถ้าแถวไหนพัง ให้ข้ามแถวนั้นไป ไม่ให้หน้าขาวทั้งหน้า
            continue
else:
    st.warning("ไม่มีข้อมูลที่จะแสดงผล")