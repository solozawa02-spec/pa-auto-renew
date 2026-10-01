# PythonAnywhere Auto-Renew Bot

บอทสำหรับต่ออายุบัญชีฟรี PythonAnywhere อัตโนมัติทุก 7 วัน ผ่าน GitHub Actions (ฟรี 100% ไม่ต้องเปิดเครื่องคอมพิวเตอร์ทิ้งไว้)

## วิธีการทำงาน
1. รันอัตโนมัติทุกวันจันทร์ เวลา 10:00 น. (เวลาไทย)
2. เข้าไปล็อกอินและกดปุ่ม "Run until..." ในแท็บ Web ของ PythonAnywhere Dashboard
3. ส่งคำสั่ง Reload Web App ผ่านทั้ง Web UI และ REST API
4. ตรวจสอบวันหมดอายุ (Expiry Date) รอบใหม่

## GitHub Secrets ที่ต้องตั้งค่า
- `PA_USERNAME`: `solozawa02`
- `PA_PASSWORD`: รหัสผ่านเข้าสู่ระบบ PythonAnywhere
- `PA_API_TOKEN`: PythonAnywhere API Token
