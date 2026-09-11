import streamlit as st
import pandas as pd
import io
import os
from datetime import datetime

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="ระบบบันทึกข้อมูลคลินิกคลายเครียด", layout="wide")

# กำหนดชื่อไฟล์สำหรับบันทึกข้อมูลให้อยู่ถาวร
DATA_FILE = "clinic_data.csv"

# ฟังก์ชันโหลดข้อมูลจากไฟล์
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=[
            "วันที่", "ชื่อ", "นามสกุล", "เพศ", "อายุ", "แดน/ห้อง", "คดี", "ครั้งที่", "ประเภทบริการ", "ผลประเมิน"
        ])

# 2. โหลดข้อมูลเมื่อเปิดเว็บ
if 'patient_data' not in st.session_state:
    st.session_state['patient_data'] = load_data()

st.title("🏥 ระบบบันทึกข้อมูลคลินิกคลายเครียด (สจ.21)")
st.markdown("ใช้สำหรับบันทึกข้อมูลผู้เข้ารับบริการ และคำนวณสรุปยอดรายงาน สจ.21 อัตโนมัติ")

tab1, tab2 = st.tabs(["📝 บันทึกข้อมูลรายบุคคล", "📊 สรุปรายงาน สจ.21"])

with tab1:
    # 3. ส่วนฟอร์มกรอกข้อมูล
    with st.form("patient_form", clear_on_submit=True):
        st.subheader("บันทึกข้อมูลผู้รับบริการ")
        col1, col2 = st.columns(2)
        
        with col1:
            fname = st.text_input("ชื่อ", placeholder="เช่น สมชาย")
            lname = st.text_input("นามสกุล", placeholder="เช่น มั่นคง")
            gender = st.radio("เพศ", ["ชาย", "หญิง"], horizontal=True)
            age = st.number_input("อายุ (ปี)", min_value=15, max_value=100, step=1)
            room = st.text_input("แดน / ห้อง", placeholder="เช่น แดน 1 / ห้อง 3")
            
        with col2:
            case_type = st.text_input("ฐานความผิด / คดี", placeholder="เช่น ลักทรัพย์, ยาเสพติด")
            visit_count = st.number_input("รับบริการครั้งที่", min_value=1, step=1)
            
            service_type = st.multiselect("ประเภทการเข้ารับบริการ (ตาม สจ.21) *เลือกได้มากกว่า 1 ข้อ", [
                "คัดกรองผู้ต้องขังเข้าใหม่",
                "ผู้ต้องขังรายเก่าที่ได้รับการคัดกรองซ้ำ",
                "ให้บริการตรวจรักษาในเรือนจำ",
                "ตรวจผ่านระบบ Telepsychiatry",
                "การบริการคลินิกคลายเครียดให้การปรึกษา",
                "เฝ้าระวังผู้ต้องขังมีพฤติกรรมเสี่ยงฆ่าตัวตาย",
                "ฆ่าตัวตายไม่สำเร็จ",
                "ฆ่าตัวตายสำเร็จ",
                "อบรมผู้ต้องขังช่วยเหลืองานด้านสุขภาพจิต"
            ])
            
            result = st.multiselect("ผลการประเมิน / การดำเนินการ *เลือกได้มากกว่า 1 ข้อ", [
                "ปกติ",
                "พบความผิดปกติ",
                "ผู้ที่พบปัญหาสุขภาพจิตและได้รับการดูแลรักษา",
                "รับการประเมินเพื่อวินิจฉัยโรคทางจิตเวช",
                "ส่งต่อไปรับการรักษานอกเรือนจำ",
                "โรงพยาบาลรับเป็นผู้ป่วยใน (admit)"
            ])
        
        submitted = st.form_submit_button("💾 บันทึกข้อมูล")
        
        if submitted:
            if fname and lname:
                service_type_str = ", ".join(service_type) if service_type else "ไม่ได้ระบุ"
                result_str = ", ".join(result) if result else "ไม่ได้ระบุ"
                
                new_data = {
                    "วันที่": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "ชื่อ": fname,
                    "นามสกุล": lname,
                    "เพศ": gender,
                    "อายุ": age,
                    "แดน/ห้อง": room,
                    "คดี": case_type,
                    "ครั้งที่": visit_count,
                    "ประเภทบริการ": service_type_str, 
                    "ผลประเมิน": result_str 
                }
                
                # นำข้อมูลใหม่ไปต่อท้ายตารางเดิม
                st.session_state['patient_data'].loc[len(st.session_state['patient_data'])] = new_data
                
                # *** บันทึกลงไฟล์ CSV ทันทีเพื่อป้องกันข้อมูลหาย ***
                st.session_state['patient_data'].to_csv(DATA_FILE, index=False)
                
                st.success(f"✅ บันทึกข้อมูลของ {fname} {lname} สำเร็จ! ข้อมูลถูกจัดเก็บอย่างปลอดภัยแล้ว")
            else:
                st.error("⚠️ กรุณากรอกชื่อและนามสกุล")

    st.subheader("📋 ตารางข้อมูลปัจจุบัน (Data Entry)")
    st.dataframe(st.session_state['patient_data'], use_container_width=True)

with tab2:
    st.subheader("📊 สรุปยอดรายงาน สจ.21 ประจำเดือน")
    df = st.session_state['patient_data']
    
    def count_data(service_kw="", result_kw="", gender=""):
        mask = pd.Series(True, index=df.index)
        if gender:
            mask = mask & (df['เพศ'] == gender)
        if service_kw:
            mask = mask & df['ประเภทบริการ'].str.contains(service_kw, na=False)
        if result_kw:
            mask = mask & df['ผลประเมิน'].str.contains(result_kw, na=False)
        return mask.sum()

    def count_unique_person(service_kw, gender):
        filtered_df = df[(df['เพศ'] == gender) & (df['ประเภทบริการ'].str.contains(service_kw, na=False))]
        return filtered_df['ชื่อ'].nunique()

    if not df.empty:
        summary_data = {
            "รายการ (ตาม สจ.21)": [
                "1. คัดกรองผู้ต้องขังเข้าใหม่", " - พบความผิดปกติ (เข้าใหม่)", " - ได้รับการดูแลรักษา (เข้าใหม่)",
                "ผู้ต้องขังรายเก่าที่ได้รับการคัดกรองซ้ำ", " - พบความผิดปกติ (รายเก่า)", " - ได้รับการดูแลรักษา (รายเก่า)",
                "2. รับการประเมินเพื่อวินิจฉัยโรคทางจิตเวช", "ให้บริการตรวจรักษาในเรือนจำ", "ตรวจผ่านระบบ Telepsychiatry",
                "ส่งต่อไปรับการรักษานอกเรือนจำ", "โรงพยาบาลรับเป็นผู้ป่วยใน (admit)",
                "3. การบริการคลินิกคลายเครียดให้การปรึกษา (จำนวนราย)", "การบริการคลินิกคลายเครียดให้การปรึกษา (จำนวนครั้ง)",
                "เฝ้าระวังผู้ต้องขังมีพฤติกรรมเสี่ยงฆ่าตัวตาย", "ฆ่าตัวตายไม่สำเร็จ", "ฆ่าตัวตายสำเร็จ",
                "อบรมผู้ต้องขังช่วยเหลืองานด้านสุขภาพจิต"
            ],
            "ชาย": [
                count_data("เข้าใหม่", "", "ชาย"), count_data("เข้าใหม่", "พบความผิดปกติ", "ชาย"), count_data("เข้าใหม่", "ได้รับการดูแลรักษา", "ชาย"),
                count_data("รายเก่า", "", "ชาย"), count_data("รายเก่า", "พบความผิดปกติ", "ชาย"), count_data("รายเก่า", "ได้รับการดูแลรักษา", "ชาย"),
                count_data("", "วินิจฉัย", "ชาย"), count_data("รักษาในเรือนจำ", "", "ชาย"), count_data("Telepsychiatry", "", "ชาย"),
                count_data("", "ส่งต่อไปรับ", "ชาย"), count_data("", "admit", "ชาย"),
                count_unique_person("ให้การปรึกษา", "ชาย"), count_data("ให้การปรึกษา", "", "ชาย"),
                count_data("เฝ้าระวัง", "", "ชาย"), count_data("ฆ่าตัวตายไม่สำเร็จ", "", "ชาย"), count_data("ฆ่าตัวตายสำเร็จ", "", "ชาย"), count_data("อบรม", "", "ชาย")
            ],
            "หญิง": [
                count_data("เข้าใหม่", "", "หญิง"), count_data("เข้าใหม่", "พบความผิดปกติ", "หญิง"), count_data("เข้าใหม่", "ได้รับการดูแลรักษา", "หญิง"),
                count_data("รายเก่า", "", "หญิง"), count_data("รายเก่า", "พบความผิดปกติ", "หญิง"), count_data("รายเก่า", "ได้รับการดูแลรักษา", "หญิง"),
                count_data("", "วินิจฉัย", "หญิง"), count_data("รักษาในเรือนจำ", "", "หญิง"), count_data("Telepsychiatry", "", "หญิง"),
                count_data("", "ส่งต่อไปรับ", "หญิง"), count_data("", "admit", "หญิง"),
                count_unique_person("ให้การปรึกษา", "หญิง"), count_data("ให้การปรึกษา", "", "หญิง"),
                count_data("เฝ้าระวัง", "", "หญิง"), count_data("ฆ่าตัวตายไม่สำเร็จ", "", "หญิง"), count_data("ฆ่าตัวตายสำเร็จ", "", "หญิง"), count_data("อบรม", "", "หญิง")
            ]
        }
        
        summary_df = pd.DataFrame(summary_data)
        st.table(summary_df)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            summary_df.to_excel(writer, index=False, sheet_name='สรุปรายงาน_สจ21')
            df.to_excel(writer, index=False, sheet_name='ข้อมูลดิบ_รายบุคคล')
            
            worksheet = writer.sheets['สรุปรายงาน_สจ21']
            worksheet.set_column('A:A', 50)
            worksheet.set_column('B:C', 15)
            
        excel_data = output.getvalue()
        
        st.download_button(
            label="📥 ดาวน์โหลดไฟล์ Excel (สรุปรายงาน + ข้อมูลดิบ)",
            data=excel_data,
            file_name="Report_SorJor21.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("ยังไม่มีข้อมูล กรุณาบันทึกข้อมูลในแท็บ 'บันทึกข้อมูลรายบุคคล' ก่อนครับ")
