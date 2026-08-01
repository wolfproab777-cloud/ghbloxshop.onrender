import os
import time
import requests
import threading
import telebot
from flask import Flask, render_template_string

# -------------------------------------------------------------
# 1. TELEGRAM BOT SOZLAMASI
# -------------------------------------------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN", "TELEGRAM_BOT_TOKENINI_SHU_YERGA_YOZING")
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start_cmd(message):
    bot.reply_to(message, "Salom! Men Render serverida 24/7 faol ishlayapman 🚀")

def run_bot():
    print("[BOT]: Telegram Bot ishga tushdi...")
    bot.infinity_polling()


# -------------------------------------------------------------
# 2. FLASK WEBSAYT SOZLAMASI
# -------------------------------------------------------------
app = Flask(__name__)

# Saytning bosh sahifasi (HTML)
HTML_LAYOUT = """
<!DOCTYPE html>
<html>
<head>
    <title>Mening 24/7 Serverim va Botim</title>
    <style>
        body { font-family: sans-serif; background: #0f172a; color: white; text-align: center; padding-top: 50px; }
        .card { background: #1e293b; padding: 30px; border-radius: 12px; display: inline-block; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
        .badge { background: #22c55e; color: black; padding: 5px 12px; border-radius: 20px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="card">
        <h1>🌐 Shaxsiy Veb-sayt & Telegram Bot</h1>
        <p>Server Holati: <span class="badge">24/7 ONLINE</span></p>
        <p>Render serverida sayt va bot bir vaqtda ishlamoqda.</p>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_LAYOUT)


# -------------------------------------------------------------
# 3. SERVERNI 24/7 UYUSHMASLIGINI TA'MINLASH (SELF-PING)
# -------------------------------------------------------------
# Render bergan sayt manzilingizni shu yerga yozasiz
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL", "https://saytingiz-nomi.onrender.com")

def keep_alive():
    """Serverni uyquga ketishidan saqlash uchun har 10 daqiqada ping yuboradi"""
    while True:
        time.sleep(600) # 10 daqiqa (600 soniya)
        try:
            print(f"[PING]: {RENDER_URL} manziliga ping yuborilmoqda...")
            requests.get(RENDER_URL)
        except Exception as e:
            print(f"[PING XATOLIK]: {e}")


# -------------------------------------------------------------
# 4. BARCHASINI BİR VAQTDA ISHGA TUSHIRISH
# -------------------------------------------------------------
if __name__ == "__main__":
    # 1. Botni alohida potokda (Thread) yurgizish
    threading.Thread(target=run_bot, daemon=True).start()

    # 2. Self-Ping mexanizmini alohida potokda yurgizish
    threading.Thread(target=keep_alive, daemon=True).start()

    # 3. Flask Serverni ishga tushirish
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
