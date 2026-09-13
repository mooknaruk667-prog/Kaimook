import streamlit as st
import pandas as pd
import io
import os
import urllib.request
from datetime import datetime
from fpdf import FPDF
from streamlit_gsheets import GSheetsConnection

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="ระบบบันทึกข้อมูลคลินิกคลายเครียด", layout="wide")

FONT_URL = "https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Regular.ttf"
FONT_PATH = "Sarabun-Regular.ttf"

@st.cache_resource
def download_font():
    if not os.path.exists(FONT_PATH):
        urllib.request.urlretrieve(FONT_URL, FONT_PATH)

download_font() 

# ================== เชื่อมต่อ Google Sheets ==================
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1wMxwcdcF3zXliTTifINkhinh76VYBh-xSj_7GLLqDxY/edit?usp=sharing"

conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        df = conn.read(spreadsheet=SPREADSHEET_URL, worksheet="Sheet1", ttl=0)
        if df.empty or len(df.columns) == 0:
            df = pd.DataFrame(columns=[
                "วันที่", "ชื่อ", "นามสกุล", "เพศ", "อายุ", "แดน/ห้อง", "คดี", "ครั้งที่", 
                "ประเภทบริการ", "ผลประเมิน", "บันทึกติดตาม", "สถานะติดตาม", "วันที่นัดติดตาม"
            ])
            conn.update(spreadsheet=SPREADSHEET_URL, worksheet="Sheet1", data=df)
        return df
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการเชื่อมต่อ Google Sheets: {e}")
        return pd.DataFrame(columns=[
            "วันที่", "ชื่อ", "นามสกุล", "เพศ", "อายุ", "แดน/ห้อง", "คดี", "ครั้งที่", 
            "ประเภทบริการ", "ผลประเมิน", "บันทึกติดตาม", "สถานะติดตาม", "วันที่นัดติดตาม"
        ])

if 'patient_data' not in st.session_state:
    st.session_state['patient_data'] = load_data()

# ตรวจสอบและบังคับเพิ่มคอลัมน์
if 'บันทึกติดตาม' not in st.session_state['patient_data'].columns:
    st.session_state['patient_data']['บันทึกติดตาม'] = ""
if 'สถานะติดตาม' not in st.session_state['patient_data'].columns:
    st.session_state['patient_data']['สถานะติดตาม'] = "รอดำเนินการ"
if 'วันที่นัดติดตาม' not in st.session_state['patient_data'].columns:
    st.session_state['patient_data']['วันที่นัดติดตาม'] = ""

st.title("🏥 ระบบบันทึกข้อมูลคลินิกคลายเครียด (สจ.21)")
st.markdown("ระบบออนไลน์ เชื่อมต่อฐานข้อมูล Cloud (ข้อมูลปลอดภัย 100%)")

tab1, tab2 = st.tabs(["📝 บันทึกข้อมูลรายบุคคล", "📊 สรุปและออกรายงาน สจ.21"])

# ================= TAB 1: บันทึกข้อมูล =================
with tab1:
    with st.form("patient_form", clear_on_submit=True):
        st.subheader("บันทึกข้อมูลผู้รับบริการ")
        col1, col2 = st.columns(2)
        
        with col1:
            fname = st.text_input("ชื่อ")
            lname = st.text_input("นามสกุล")
            gender = st.radio("เพศ", ["ชาย", "หญิง"], horizontal=True)
            age = st.number_input("อายุ (ปี)", min_value=15, max_value=100, step=1)
            room = st.text_input("แดน / ห้อง")
            
        with col2:
            case_type = st.text_input("ฐานความผิด / คดี")
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
        
        submitted = st.form_submit_button("💾 บันทึกข้อมูลใหม่")
        if submitted:
            if fname and lname:
                service_type_str = ", ".join(service_type) if service_type else "ไม่ได้ระบุ"
                result_str = ", ".join(result) if result else "ไม่ได้ระบุ"
                
                new_data = {
                    "วันที่": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "ชื่อ": fname, "นามสกุล": lname, "เพศ": gender, "อายุ": age,
                    "แดน/ห้อง": room, "คดี": case_type, "ครั้งที่": visit_count,
                    "ประเภทบริการ": service_type_str, "ผลประเมิน": result_str,
                    "บันทึกติดตาม": "", "สถานะติดตาม": "รอดำเนินการ", "วันที่นัดติดตาม": ""
                }
                
                st.session_state['patient_data'].loc[len(st.session_state['patient_data'])] = new_data
                conn.update(spreadsheet=SPREADSHEET_URL, worksheet="Sheet1", data=st.session_state['patient_data'])
                
                st.success(f"✅ บันทึกข้อมูลของ {fname} {lname} ขึ้นฐานข้อมูลสำเร็จ!")
            else:
                st.error("⚠️ กรุณากรอกชื่อและนามสกุล")

    # ================= ส่วนตารางที่แก้ไขได้ =================
    st.markdown("---")
    st.subheader("📋 ตารางข้อมูลปัจจุบัน (สามารถแก้ไขข้อมูลในตารางได้โดยตรง)")
    st.info("💡 **วิธีใช้งาน:** ดับเบิลคลิกที่ช่องเพื่อพิมพ์แก้ไขหรือเลือก Drop-down และสามารถคลิกเลือกแถวเพื่อลบข้อมูลได้ เมื่อแก้เสร็จแล้วให้กดปุ่ม **'ยืนยันการแก้ไข'** ด้านล่าง")
    
    df_current = st.session_state['patient_data']
    
    if not df_current.empty:
        edited_df = st.data_editor(
            df_current, 
            num_rows="dynamic", 
            use_container_width=True,
            column_config={
                "เพศ": st.column_config.SelectboxColumn("เพศ", options=["ชาย", "หญิง"]),
                "ประเภทบริการ": st.column_config.SelectboxColumn(
                    "ประเภทบริการ",
                    options=[
                        "คัดกรองผู้ต้องขังเข้าใหม่", "ผู้ต้องขังรายเก่าที่ได้รับการคัดกรองซ้ำ",
                        "ให้บริการตรวจรักษาในเรือนจำ", "ตรวจผ่านระบบ Telepsychiatry",
                        "การบริการคลินิกคลายเครียดให้การปรึกษา", "เฝ้าระวังผู้ต้องขังมีพฤติกรรมเสี่ยงฆ่าตัวตาย",
                        "ฆ่าตัวตายไม่สำเร็จ", "ฆ่าตัวตายสำเร็จ", "อบรมผู้ต้องขังช่วยเหลืองานด้านสุขภาพจิต"
                    ]
                ),
                "ผลประเมิน": st.column_config.SelectboxColumn(
                    "ผลประเมิน",
                    options=[
                        "ปกติ", "พบความผิดปกติ", "ผู้ที่พบปัญหาสุขภาพจิตและได้รับการดูแลรักษา",
                        "รับการประเมินเพื่อวินิจฉัยโรคทางจิตเวช", "ส่งต่อไปรับการรักษานอกเรือนจำ",
                        "โรงพยาบาลรับเป็นผู้ป่วยใน (admit)"
                    ]
                ),
                "สถานะติดตาม": st.column_config.SelectboxColumn(
                    "สถานะติดตาม",
                    options=["รอดำเนินการ", "ติดตามแล้ว", "ติดตามต่อ", "ปิดเคส", "บันทึกครั้งใหม่แล้ว"]
                )
            }
        )
        
        if st.button("💾 ยืนยันการแก้ไขและบันทึกลงฐานข้อมูล"):
            st.session_state['patient_data'] = edited_df
            conn.update(spreadsheet=SPREADSHEET_URL, worksheet="Sheet1", data=edited_df)
            st.success("✅ บันทึกการแก้ไขทั้งหมดลง Google Sheets เรียบร้อยแล้ว!")
            st.rerun()
    else:
        st.dataframe(df_current, use_container_width=True)

    # ================= ส่วนแจ้งเตือนติดตามผู้ป่วย =================
    st.markdown("---")
    st.subheader("🔔 แจ้งเตือนเคสที่ต้องติดตามต่อ")
    if not df_current.empty:
        to_follow_up = st.session_state['patient_data'][st.session_state['patient_data']['สถานะติดตาม'] == 'ติดตามต่อ']
        if not to_follow_up.empty:
            for idx, row in to_follow_up.iterrows():
                date_str = row['วันที่นัดติดตาม'] if pd.notna(row['วันที่นัดติดตาม']) and row['วันที่นัดติดตาม'] != "" else "ไม่ได้ระบุวัน"
                st.warning(f"📅 **นัดติดตามอาการ:** {row['ชื่อ']} {row['นามสกุล']} (แดน: {row['แดน/ห้อง']}) — นัดหมายวันที่: **{date_str}**")
        else:
            st.info("🎉 ปัจจุบันไม่มีเคสที่ค้างการติดตาม")

    # ================= ส่วนระบบติดตามผู้ป่วย (Follow-up) =================
    st.markdown("---")
    st.subheader("🚨 ระบบอัปเดตสถานะผู้ป่วย")
    
    if not df_current.empty:
        abnormal_patients = st.session_state['patient_data'][
            (st.session_state['patient_data']['ผลประเมิน'].astype(str).str.contains("พบความผิดปกติ", na=False)) &
            (st.session_state['patient_data']['สถานะติดตาม'] != "บันทึกครั้งใหม่แล้ว")
        ]
        
        if not abnormal_patients.empty:
            for idx, row in abnormal_patients.iterrows():
                status_icon = "🟢" if row['สถานะติดตาม'] == "ปิดเคส" else ("🟡" if row['สถานะติดตาม'] == "ติดตามต่อ" else "🔴")
                
                with st.expander(f"{status_icon} อัปเดตอาการ: {row['ชื่อ']} {row['นามสกุล']} [สถานะ: {row['สถานะติดตาม']}]"):
                    st.write(f"**วันที่รับบริการล่าสุด:** {row['วันที่']} | **เข้ารับบริการครั้งที่:** {row['ครั้งที่']}")
                    
                    # 1. อัปเดต "ประเภทการเข้ารับบริการ"
                    valid_srv_options = [
                        "คัดกรองผู้ต้องขังเข้าใหม่", "ผู้ต้องขังรายเก่าที่ได้รับการคัดกรองซ้ำ",
                        "ให้บริการตรวจรักษาในเรือนจำ", "ตรวจผ่านระบบ Telepsychiatry",
                        "การบริการคลินิกคลายเครียดให้การปรึกษา", "เฝ้าระวังผู้ต้องขังมีพฤติกรรมเสี่ยงฆ่าตัวตาย",
                        "ฆ่าตัวตายไม่สำเร็จ", "ฆ่าตัวตายสำเร็จ", "อบรมผู้ต้องขังช่วยเหลืองานด้านสุขภาพจิต"
                    ]
                    old_srv = [s.strip() for s in str(row.get('ประเภทบริการ', '')).split(",")]
                    default_srv = [s for s in old_srv if s in valid_srv_options]
                    new_service_list = st.multiselect("ประเภทการเข้ารับบริการ (ครั้งนี้)", valid_srv_options, default=default_srv, key=f"srv_{idx}")
                    new_service_str = ", ".join(new_service_list) if new_service_list else "ไม่ได้ระบุ"

                    # 2. อัปเดต "ผลประเมิน"
                    valid_res_options = ["ปกติ", "พบความผิดปกติ", "ผู้ที่พบปัญหาสุขภาพจิตและได้รับการดูแลรักษา", "รับการประเมินเพื่อวินิจฉัยโรคทางจิตเวช", "ส่งต่อไปรับการรักษานอกเรือนจำ", "โรงพยาบาลรับเป็นผู้ป่วยใน (admit)"]
                    old_res = [r.strip() for r in str(row.get('ผลประเมิน', '')).split(",")]
                    default_res = [r for r in old_res if r in valid_res_options]
                    new_result_list = st.multiselect("ผลประเมิน (อัปเดตล่าสุด)", valid_res_options, default=default_res, key=f"res_{idx}")
                    new_result_str = ", ".join(new_result_list) if new_result_list else "ไม่ได้ระบุ"

                    # 3. เลือกสถานะ
                    status_options = ["รอดำเนินการ", "ติดตามแล้ว", "ติดตามต่อ", "ปิดเคส"]
                    current_status = row['สถานะติดตาม'] if pd.notna(row['สถานะติดตาม']) else "รอดำเนินการ"
                    status_idx = status_options.index(current_status) if current_status in status_options else 0
                    new_status = st.selectbox("สถานะการติดตาม", status_options, index=status_idx, key=f"status_{idx}")
                    
                    # 4. เลือกวันนัด
                    new_date_str = row['วันที่นัดติดตาม']
                    if new_status == "ติดตามต่อ":
                        parsed_date = datetime.now().date()
                        if pd.notna(row['วันที่นัดติดตาม']) and str(row['วันที่นัดติดตาม']).strip() != "":
                            try:
                                parsed_date = datetime.strptime(str(row['วันที่นัดติดตาม']), "%Y-%m-%d").date()
                            except ValueError:
                                pass
                        
                        selected_date = st.date_input("ระบุวันที่นัดติดตามครั้งต่อไป", value=parsed_date, key=f"date_{idx}")
                        new_date_str = selected_date.strftime("%Y-%m-%d")
                    else:
                        new_date_str = "" 
                    
                    # 5. บันทึกข้อความ
                    current_note = row['บันทึกติดตาม'] if pd.notna(row['บันทึกติดตาม']) else ""
                    new_note = st.text_area("บันทึกความคืบหน้าของอาการ:", value=current_note, key=f"note_{idx}")
                    
                    # 6. ตั้งค่าการบวกจำนวนครั้ง
                    next_visit_num = 2
                    if pd.notna(row['ครั้งที่']):
                        try:
                            next_visit_num = int(row['ครั้งที่']) + 1
                        except ValueError:
                            pass
                    
                    create_new_visit = st.checkbox(f"✅ บันทึกเป็นประวัติการเข้ารับบริการครั้งใหม่ (ปรับเป็นครั้งที่ {next_visit_num})", value=True, key=f"new_visit_{idx}")
                    
                    if st.button("💾 บันทึกอัปเดต", key=f"save_note_{idx}"):
                        if create_new_visit:
                            st.session_state['patient_data'].at[idx, 'สถานะติดตาม'] = "บันทึกครั้งใหม่แล้ว"
                            
                            new_row = row.copy()
                            new_row['วันที่'] = datetime.now().strftime("%d/%m/%Y %H:%M")
                            new_row['ครั้งที่'] = next_visit_num
                            new_row['ประเภทบริการ'] = new_service_str
                            new_row['ผลประเมิน'] = new_result_str
                            new_row['บันทึกติดตาม'] = new_note
                            new_row['สถานะติดตาม'] = new_status
                            new_row['วันที่นัดติดตาม'] = new_date_str
                            
                            st.session_state['patient_data'].loc[len(st.session_state['patient_data'])] = new_row
                        else:
                            st.session_state['patient_data'].at[idx, 'ประเภทบริการ'] = new_service_str
                            st.session_state['patient_data'].at[idx, 'ผลประเมิน'] = new_result_str
                            st.session_state['patient_data'].at[idx, 'บันทึกติดตาม'] = new_note
                            st.session_state['patient_data'].at[idx, 'สถานะติดตาม'] = new_status
                            st.session_state['patient_data'].at[idx, 'วันที่นัดติดตาม'] = new_date_str
                        
                        conn.update(spreadsheet=SPREADSHEET_URL, worksheet="Sheet1", data=st.session_state['patient_data'])
                        st.success("บันทึกการติดตามเรียบร้อยแล้ว!")
                        st.rerun() 
        else:
            st.success("ไม่มีผู้ป่วยที่พบความผิดปกติที่ต้องติดตาม")

# ================= TAB 2: สรุปรายงาน สจ.21 =================
with tab2:
    st.subheader("⚙️ ตั้งค่ารายงาน (ข้อมูลส่วนหัวและส่วนท้าย)")
    
    col_m, col_y, col_d = st.columns(3)
    with col_m:
        months_th = ["มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน", "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]
        report_month = st.selectbox("ประจำเดือน", months_th, index=datetime.now().month-1)
    with col_y:
        current_year_th = datetime.now().year + 543
        report_year = st.number_input("ปี (พ.ศ.)", value=current_year_th, step=1)
    with col_d:
        report_date = st.date_input("ข้อมูล ณ วันที่", datetime.now())
        
    col_act1, col_act2 = st.columns([3, 1])
    with col_act1:
        other_act_name = st.text_input("กิจกรรมส่งเสริมสุขภาพจิตอื่นๆ (ระบุชื่อกิจกรรม)", placeholder="เช่น จัดบอร์ดความรู้, เสียงตามสาย...")
    with col_act2:
        other_act_count = st.number_input("จำนวน (ครั้ง)", min_value=0, step=1)
        
    problems = st.text_area("4. ปัญหาและอุปสรรคที่พบ (ถ้ามี)", placeholder="พิมพ์ปัญหาหรืออุปสรรคที่นี่...")

    df = st.session_state['patient_data']
    
    def count_data(service_kw="", result_kw="", gender=""):
        mask = pd.Series(True, index=df.index)
        if gender: mask = mask & (df.get('เพศ', '') == gender)
        if service_kw: mask = mask & df.get('ประเภทบริการ', pd.Series(dtype=str)).astype(str).str.contains(service_kw, na=False)
        if result_kw: mask = mask & df.get('ผลประเมิน', pd.Series(dtype=str)).astype(str).str.contains(result_kw, na=False)
        return mask.sum()

    def count_unique_person(service_kw, gender):
        if 'เพศ' not in df.columns or 'ประเภทบริการ' not in df.columns or 'ชื่อ' not in df.columns: return 0
        filtered_df = df[(df['เพศ'] == gender) & (df['ประเภทบริการ'].astype(str).str.contains(service_kw, na=False))]
        return filtered_df['ชื่อ'].nunique()

    if not df.empty:
        st.markdown("---")
        st.subheader("📊 หน้าตาของตารางรายงานที่จะถูกสร้าง")
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
        
        def generate_pdf():
            pdf = FPDF()
            pdf.add_page()
            
            if os.path.exists(FONT_PATH):
                pdf.add_font("Sarabun", style="", fname=FONT_PATH)
                pdf.set_font("Sarabun", size=18)
            else:
                pdf.set_font("Arial", size=16)

            pdf.cell(0, 10, "แบบรายงานการดำเนินงานคลินิกคลายเครียด", ln=True, align="C")
            pdf.set_font("Sarabun", size=16)
            pdf.cell(0, 10, f"เรือนจำจังหวัดบุรีรัมย์ ประจำเดือน {report_month} พ.ศ. {report_year}", ln=True, align="C")
            date_str = report_date.strftime("%d/%m/%Y")
            pdf.set_font("Sarabun", size=14)
            pdf.cell(0, 10, f"(ข้อมูล ณ วันที่ {date_str})", ln=True, align="C")
            pdf.ln(5)

            pdf.set_font("Sarabun", size=14)
            for idx, row in summary_df.iterrows():
                item = row["รายการ (ตาม สจ.21)"]
                m = row["ชาย"]
                f = row["หญิง"]
                pdf.cell(130, 8, txt=item, border=0)
                pdf.cell(30, 8, txt=f"ชาย: {m} ราย", border=0)
                pdf.cell(30, 8, txt=f"หญิง: {f} ราย", border=0, ln=True)

            pdf.ln(5)
            pdf.set_font("Sarabun", size=15)
            act_text = other_act_name if other_act_name.strip() else "- ไม่ได้ระบุ -"
            pdf.cell(0, 10, txt=f"กิจกรรมส่งเสริมสุขภาพจิตอื่นๆ (ระบุ): {act_text}    จำนวน {other_act_count} ครั้ง", ln=True)
            pdf.cell(0, 10, txt="4. ปัญหาและอุปสรรคที่พบ (ถ้ามี):", ln=True)
            
            pdf.set_font("Sarabun", size=14)
            pdf.multi_cell(0, 8, txt=problems if problems.strip() else "- ไม่มี -")
            
            pdf.ln(20)
            pdf.cell(0, 10, txt="ลงชื่อ.......................................................", ln=True, align="R")
            pdf.cell(0, 10, txt="ผู้ให้การปรึกษา/ทีมสุขภาพจิตเรือนจำ", ln=True, align="R")
            
            return bytes(pdf.output())

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
