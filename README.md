# LINE + FastAPI + Ollama + RAG

## เตรียมระบบ
1) ติดตั้ง Python 3.10–3.12 (แนะนำ 3.10/3.11)
2) `python -m venv venv && source venv/bin/activate` (Windows: `venv\Scripts\activate`)
3) `pip install -r requirements.txt`
4) ติดตั้ง Ollama และดึงโมเดล:
   - `ollama pull llama3`
   - `ollama pull nomic-embed-text`
5) สร้างไฟล์ `.env` อิงจากตัวอย่าง และใส่ CHANNEL_SECRET / ACCESS_TOKEN
6) ใส่เอกสารไว้ใน `./data`

## รันระบบ
1) เปิด Ollama (ต้องให้ service ฟังที่พอร์ต 11434)
   - พอมี ollama อยู่แล้ว ส่วนใหญ่ไม่ต้องสั่งอะไรเพิ่ม
   - ทดสอบ: `curl http://localhost:11434/api/tags`
2) รัน FastAPI
   - `uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`
3) เปิด ngrok:
   - `ngrok http 8000`
   - เอา URL จาก ngrok ไปตั้งใน LINE Developer Console → Messaging API → Webhook URL → `https://<your-ngrok>.ngrok-free.app/webhook`
4) ทดสอบพิมพ์ใน LINE OA
   - คำสั่งพิเศษ: `"/refresh"` เพื่อรีโหลดดัชนีจากโฟลเดอร์ `data/`

## ทิปส์
- ถ้าเปลี่ยน/เพิ่มไฟล์ใน `data/` ให้พิมพ์ใน LINE: `/refresh`
- ถ้าเจอ error embeddings: ตรวจว่า `ollama pull nomic-embed-text` แล้ว
- ถ้าเว็บฮุคไม่ยิง: ตรวจ `X-Line-Signature` (อย่าลืมส่ง header เข้า parser)
