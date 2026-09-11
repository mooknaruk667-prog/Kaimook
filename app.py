import streamlit as st
import pandas as pd
import io
import os
import urllib.request
from datetime import datetime
from fpdf import FPDF

# 1. ตั้งค่าหน้าเว็บและฟอนต์ภาษาไทยสำหรับ PDF
st.set_page_config(page_title="ระบบบันทึกข้อมูลคลินิกคลายเครียด", layout="wide")

FONT_URL = "https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Regular.ttf"
FONT_PATH = "Sarabun-Regular.ttf"

@st.cache_resource
def download_font():
    if not os.path.exists(FONT_PATH):
        urllib.request.urlretrieve(FONT_URL, FONT_PATH)

download_font() # สั่งโหลดฟอนต์อัตโนมัติเมื่อเปิดเว็บ

DATA_FILE = "clinic_data.csv"

# ฟังก์ชันโหลดข้อมูล
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=[
            "วันที่", "ชื่อ", "นามสกุล", "เพศ", "อายุ", "แดน/ห้อง", "คดี", "ครั้งที่", "ประเภทบริการ", "ผลประเมิน"
        ])

if 'patient_data' not in st.session_state:
    st.session_state['patient_data'] = load_data()

st.title("🏥 ระบบบันทึกข้อมูลคลินิกคลายเครียด (สจ.21)")
st.markdown("ใช้สำหรับบันทึกข้อมูลผู้เข้ารับบริการ และออกรายงาน สจ.21 เป็นไฟล์ Excel และ PDF")

tab1, tab2 = st.tabs(["📝 บันทึกข้อมูลรายบุคคล", "📊 สรุปและออกรายงาน สจ.21"])

# ================= TAB 1: บันทึกข้อมูล =================
with tab1:
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
            
            service_type = st.multiselect("ประเภทการเข้ารับบริการ (ตาม สจ.21)", [
                "คัดกรองผู้ต้องขังเข้าใหม่", "ผู้ต้องขังรายเก่าที่ได้รับการคัดกรองซ้ำ",
                "ให้บริการตรวจรักษาในเรือนจำ", "ตรวจผ่านระบบ Telepsychiatry",
                "การบริการคลินิกคลายเครียดให้การปรึกษา", "เฝ้าระวังผู้ต้องขังมีพฤติกรรมเสี่ยงฆ่าตัวตาย",
                "ฆ่าตัวตายไม่สำเร็จ", "ฆ่าตัวตายสำเร็จ", "อบรมผู้ต้องขังช่วยเหลืองานด้านสุขภาพจิต"
            ])
            
            result = st.multiselect("ผลการประเมิน / การดำเนินการ", [
                "ปกติ", "พบความผิดปกติ", "ผู้ที่พบปัญหาสุขภาพจิตและได้รับการดูแลรักษา",
                "รับการประเมินเพื่อวินิจฉัยโรคทางจิตเวช", "ส่งต่อไปรับการรักษานอกเรือนจำ",
                "โรงพยาบาลรับเป็นผู้ป่วยใน (admit)"
            ])
        
        submitted = st.form_submit_button("💾 บันทึกข้อมูล")
        if submitted:
            if fname and lname:
                service_type_str = ", ".join(service_type) if service_type else "ไม่ได้ระบุ"
                result_str = ", ".join(result) if result else "ไม่ได้ระบุ"
                
                new_data = {
                    "วันที่": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "ชื่อ": fname, "นามสกุล": lname, "เพศ": gender, "อายุ": age,
                    "แดน/ห้อง": room, "คดี": case_type, "ครั้งที่": visit_count,
                    "ประเภทบริการ": service_type_str, "ผลประเมิน": result_str 
                }
                
                st.session_state['patient_data'].loc[len(st.session_state['patient_data'])] = new_data
                st.session_state['patient_data'].to_csv(DATA_FILE, index=False)
                st.success(f"✅ บันทึกข้อมูลของ {fname} {lname} สำเร็จ!")
            else:
                st.error("⚠️ กรุณากรอกชื่อและนามสกุล")

    st.subheader("📋 ตารางข้อมูลปัจจุบัน")
    st.dataframe(st.session_state['patient_data'], use_container_width=True)


# ================= TAB 2: สรุปรายงาน สจ.21 =================
with tab2:
    st.subheader("⚙️ ตั้งค่ารายงาน (ข้อมูลส่วนหัวและส่วนท้าย)")
    
    # 1. รับข้อมูลสำหรับการออกรายงาน
    col_m, col_y, col_d = st.columns(3)
    with col_m:
        months_th = ["มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน", "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]
        report_month = st.selectbox("ประจำเดือน", months_th, index=datetime.now().month-1)
    with col_y:
        current_year_th = datetime.now().year + 543
        report_year = st.number_input("ปี (พ.ศ.)", value=current_year_th, step=1)
    with col_d:
        report_date = st.date_input("ข้อมูล ณ วันที่", datetime.now())
        
    other_act = st.number_input("กิจกรรมส่งเสริมสุขภาพจิตอื่นๆ (จำนวน/ครั้ง)", min_value=0, step=1)
    problems = st.text_area("4. ปัญหาและอุปสรรคที่พบ (ถ้ามี)", placeholder="พิมพ์ปัญหาหรืออุปสรรคที่นี่...")

    # 2. คำนวณสรุปยอด
    df = st.session_state['patient_data']
    
    def count_data(service_kw="", result_kw="", gender=""):
        mask = pd.Series(True, index=df.index)
        if gender: mask = mask & (df['เพศ'] == gender)
        if service_kw: mask = mask & df['ประเภทบริการ'].str.contains(service_kw, na=False)
        if result_kw: mask = mask & df['ผลประเมิน'].str.contains(result_kw, na=False)
        return mask.sum()

    def count_unique_person(service_kw, gender):
        filtered_df = df[(df['เพศ'] == gender) & (df['ประเภทบริการ'].str.contains(service_kw, na=False))]
        return filtered_df['ชื่อ'].nunique()

    if not df.empty:
        st.markdown("---")
        st.subheader("📊 หน้าตาของรายงานที่จะถูกสร้าง")
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
        
        # 3. ฟังก์ชันสร้าง PDF
        def generate_pdf():
            pdf = FPDF()
            pdf.add_page()
            
            # ตรวจสอบและตั้งค่าฟอนต์ไทย
            if os.path.exists(FONT_PATH):
                pdf.add_font("Sarabun", style="", fname=FONT_PATH)
                pdf.set_font("Sarabun", size=18)
            else:
                pdf.set_font("Arial", size=16)

            # ส่วนหัวรายงาน
            pdf.cell(0, 10, "แบบรายงานการดำเนินงานคลินิกคลายเครียด", ln=True, align="C")
            pdf.set_font("Sarabun", size=16)
            pdf.cell(0, 10, f"เรือนจำจังหวัดบุรีรัมย์ ประจำเดือน {report_month} พ.ศ. {report_year}", ln=True, align="C")
            date_str = report_date.strftime("%d/%m/%Y")
            pdf.set_font("Sarabun", size=14)
            pdf.cell(0, 10, f"(ข้อมูล ณ วันที่ {date_str})", ln=True, align="C")
            pdf.ln(5)

            # ส่วนเนื้อหา (ตารางสรุป)
            pdf.set_font("Sarabun", size=14)
            for idx, row in summary_df.iterrows():
                item = row["รายการ (ตาม สจ.21)"]
                m = row["ชาย"]
                f = row["หญิง"]
                
                # จัดรูปแบบให้เหมือนตารางบรรทัดต่อบรรทัด
                pdf.cell(130, 8, txt=item, border=0)
                pdf.cell(30, 8, txt=f"ชาย: {m} ราย", border=0)
                pdf.cell(30, 8, txt=f"หญิง: {f} ราย", border=0, ln=True)

            # ส่วนท้าย (ข้อมูลเพิ่มเติมที่ผู้ใช้ขอ)
            pdf.ln(5)
            pdf.set_font("Sarabun", size=15)
            pdf.cell(0, 10, txt=f"กิจกรรมส่งเสริมสุขภาพจิตอื่นๆ: {other_act} ครั้ง", ln=True)
            pdf.cell(0, 10, txt="4. ปัญหาและอุปสรรคที่พบ (ถ้ามี):", ln=True)
            
            pdf.set_font("Sarabun", size=14)
            # ตัดบรรทัดอัตโนมัติหากข้อความยาว
            pdf.multi_cell(0, 8, txt=problems if problems.strip() else "- ไม่มี -")
            
            pdf.ln(20)
            pdf.cell(0, 10, txt="ลงชื่อ.......................................................", ln=True, align="R")
            pdf.cell(0, 10, txt="ผู้ให้การปรึกษา/ทีมสุขภาพจิตเรือนจำ", ln=True, align="R")
            
            return bytes(pdf.output())

        # 4. ปุ่มดาวน์โหลด
        st.markdown("### 📥 ดาวน์โหลดรายงาน")
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            output_excel = io.BytesIO()
            with pd.ExcelWriter(output_excel, engine='xlsxwriter') as writer:
                summary_df.to_excel(writer, index=False, sheet_name='สรุปรายงาน_สจ21')
                df.to_excel(writer, index=False, sheet_name='ข้อมูลดิบ')
            st.download_button("📥 ดาวน์โหลด Excel", data=output_excel.getvalue(), file_name=f"Report_Sj21_{report_month}.xlsx")
            
        with col_btn2:
            try:
                pdf_bytes = generate_pdf()
                st.download_button("📄 ดาวน์โหลด PDF (พร้อมพิมพ์)", data=pdf_bytes, file_name=f"Report_Sj21_{report_month}.pdf", mime="application/pdf")
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาดในการสร้าง PDF: {e}")
                
    else:
        st.info("ยังไม่มีข้อมูล กรุณาบันทึกข้อมูลในแท็บ 'บันทึกข้อมูลรายบุคคล' ก่อนครับ")
