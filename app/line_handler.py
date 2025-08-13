from fastapi import Request
from fastapi.responses import JSONResponse
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

from app.config import CHANNEL_SECRET, CHANNEL_ACCESS_TOKEN
from app.rag_agent import answer_query, refresh_index

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(CHANNEL_SECRET)

async def handle_line_webhook(request: Request):
    signature = request.headers.get("X-Line-Signature", "")
    body_bytes = await request.body()
    body = body_bytes.decode("utf-8")

    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        return JSONResponse(status_code=400, content={"error": "Invalid signature"})

    for event in events:
        if isinstance(event, MessageEvent) and isinstance(event.message, TextMessage):
            user_msg = event.message.text.strip()

            # คำสั่งพิเศษในแชท
            if user_msg.lower() in ("/refresh", "refresh", "รีเฟรช"):
                reply_text = refresh_index()

            elif user_msg.lower().startswith("/debug"):
                reply_text = answer_query("สรุปสาระสำคัญของเอกสารนี้ 3 ข้อ")
                
            else:
                reply_text = answer_query(user_msg)

            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=reply_text[:4900])  # กันยาวเกิน
            )

    return JSONResponse(content={"status": "ok"})
