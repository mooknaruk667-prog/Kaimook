# ระบบบันทึกข้อมูลคลินิกคลายเครียด (Streamlit App)

โปรเจกต์นี้เขียนด้วย Python (Streamlit) เพื่อใช้สร้างแบบฟอร์มบันทึกข้อมูลผู้ต้องขังที่เข้ารับบริการคลินิกคลายเครียด (ตามแบบฟอร์ม สจ.21) และสามารถ Export ข้อมูลออกมาเป็นไฟล์ Excel ได้

## ไฟล์ในโปรเจกต์
- `app.py`: โค้ดหลักของเว็บไซต์ (ฟอร์มและตารางข้อมูล)
- `requirements.txt`: รายชื่อ Library ที่จำเป็นสำหรับการรันโค้ดบน Server

## วิธีการนำโค้ดขึ้น GitHub และเปิดใช้งานเว็บไซต์ (Deploy) ฟรี!

1. **สร้าง Repository ใน GitHub:**
   - สมัครและเข้าสู่ระบบ [GitHub](https://github.com/)
   - กดปุ่ม **New** เพื่อสร้าง Repository ใหม่ (ตั้งชื่อเช่น `prison-clinic-app`)
   - อัปโหลดไฟล์ `app.py` และ `requirements.txt` ลงไปใน Repository นี้ แล้วกด Commit

2. **เปิดใช้งานเว็บไซต์ (Deploy) ด้วย Streamlit Cloud:**
   - ไปที่ [Streamlit Community Cloud](https://share.streamlit.io/) และ Log in ด้วยบัญชี GitHub ของคุณ
   - กดปุ่ม **New app** (หรือ Create app)
   - ในช่อง Repository ให้พิมพ์หรือเลือกชื่อ Repository ที่เพิ่งสร้าง (`prison-clinic-app`)
   - ช่อง Branch เลือก `main`
   - ช่อง Main file path พิมพ์ `app.py`
   - กดปุ่ม **Deploy!**

รอระบบตั้งค่าประมาณ 1-2 นาที คุณก็จะได้ลิงก์เว็บไซต์ของตัวเองที่สามารถส่งให้เจ้าหน้าที่คนอื่นๆ ใช้งานและโหลด Excel ได้ทันทีครับ!
