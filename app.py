import streamlit as st
import pandas as pd
import io
from datetime import datetime

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="ระบบบันทึกข้อมูลคลินิกคลายเครียด", layout="wide")

# 2. สร้างที่เก็บข้อมูลชั่วคราว
if 'patient_data' not in st.session_state:
    st.session_state['patient_data'] = pd.DataFrame(columns=[
        "วันที่", "ชื่อ", "นามสกุล", "เพศ", "อายุ", "แดน/ห้อง", "คดี", "ครั้งที่", "ประเภทบริการ", "ผลประเมิน"
    ])

st.title("🏥 ระบบบันทึกข้อมูลคลินิกคลายเครียด (สจ.21)")
st.markdown("ใช้สำหรับบันทึกข้อมูลผู้เข้ารับบริการและส่งออกเป็นไฟล์ Excel เพื่อจัดทำรายงาน สจ.21")

# 3. ส่วนฟอร์มกรอกข้อมูล
with st.form("patient_form", clear_on_submit=True):
    st.subheader("📝 บันทึกข้อมูลผู้รับบริการ")
    
    col1, col2 = st.columns(2)
    
    # --- คอลัมน์ซ้าย ---
    with col1:
        fname = st.text_input("ชื่อ", placeholder="เช่น สมชาย")
        lname = st.text_input("นามสกุล", placeholder="เช่น มั่นคง")
        gender = st.radio("เพศ", ["ชาย", "หญิง"], horizontal=True)
        age = st.number_input("อายุ (ปี)", min_value=15, max_value=100, step=1)
        room = st.text_input("แดน / ห้อง", placeholder="เช่น แดน 1 / ห้อง 3")
        
    # --- คอลัมน์ขวา ---
    with col2:
        case_type = st.text_input("ฐานความผิด / คดี", placeholder="เช่น ลักทรัพย์, ยาเสพติด")
        visit_count = st.number_input("รับบริการครั้งที่", min_value=1, step=1)
        
        # อัปเดต: เปลี่ยนเป็น multiselect ให้เลือกได้มากกว่า 1 ข้อ
        service_type = st.multiselect("ประเภทการเข้ารับบริการ (ตาม สจ.21) *เลือกได้มากกว่า 1 ข้อ", [
            "1. คัดกรองผู้ต้องขังเข้าใหม่",
            "2. คัดกรองซ้ำ (รายเก่า)",
            "3. ตรวจรักษาในเรือนจำ",
            "4. ตรวจผ่านระบบ Telepsychiatry",
            "5. ให้การปรึกษาคลินิกคลายเครียด",
            "6. เฝ้าระวังผู้ต้องขังมีพฤติกรรมเสี่ยงฆ่าตัวตาย"
        ])
        
        result = st.selectbox("ผลการประเมิน / การดำเนินการ", [
            "ปกติ",
            "พบความผิดปกติ",
            "ผู้ที่พบปัญหาสุขภาพจิตและได้รับการดูแลรักษา",
            "ส่งต่อรับการรักษานอกเรือนจำ",
            "โรงพยาบาลรับเป็นผู้ป่วยใน (admit)",
            "รับการประเมินเพื่อวินิจฉัยโรคทางจิตเวช"
        ])
    
    # 4. ปุ่มบันทึกข้อมูล
    submitted = st.form_submit_button("💾 บันทึกข้อมูล")
    
    if submitted:
        if fname and lname:
            # นำข้อมูลที่เลือกหลายข้อมาต่อกันด้วยคอมม่า (,)
            service_type_str = ", ".join(service_type) if service_type else "ไม่ได้ระบุ"
            
            new_data = {
                "วันที่": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "ชื่อ": fname,
                "นามสกุล": lname,
                "เพศ": gender,
                "อายุ": age,
                "แดน/ห้อง": room,
                "คดี": case_type,
                "ครั้งที่": visit_count,
                "ประเภทบริการ": service_type_str, # บันทึกเป็นข้อความที่รวมแล้ว
                "ผลประเมิน": result
            }
            # เพิ่มข้อมูลใหม่ลงในตาราง
            st.session_state['patient_data'].loc[len(st.session_state['patient_data'])] = new_data
            st.success(f"✅ บันทึกข้อมูลของ {fname} {lname} สำเร็จ!")
        else:
            st.error("⚠️ กรุณากรอกชื่อและนามสกุล")

# 5. ส่วนแสดงผลตาราง
st.subheader("📋 ตารางข้อมูลปัจจุบัน")
st.dataframe(st.session_state['patient_data'], use_container_width=True)

# 6. ส่วนการ Export เป็น Excel
if not st.session_state['patient_data'].empty:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        st.session_state['patient_data'].to_excel(writer, index=False, sheet_name='สจ21_Data')
    excel_data = output.getvalue()
    
    st.download_button(
        label="📥 ดาวน์โหลดข้อมูลทั้งหมดเป็นไฟล์ Excel",
        data=excel_data,
        file_name="clinic_data_export.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
