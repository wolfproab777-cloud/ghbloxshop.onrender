import os
import threading
import time
import requests
from datetime import datetime
import pytz
from flask import Flask, render_template_string
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# -------------------------------------------------------------
# 1. AKSIYA VA NARX MANTIQI (Tashkent vaqti bilan UTC+5)
# -------------------------------------------------------------
ORIGINAL_PRICE = 32000
DISCOUNT_PERCENT = 10  # 10% chegirma

def get_current_price_info():
    """Hozirgi vaqtga qarab narx va aksiya holatini aniqlaydi"""
    tz = pytz.timezone('Asia/Tashkent')
    now = datetime.now(tz)
    
    # 15:30 dan 17:30 gacha aksiya vaqti
    start_time = now.replace(hour=15, minute=30, second=0, microsecond=0)
    end_time = now.replace(hour=17, minute=30, second=0, microsecond=0)
    
    if start_time <= now <= end_time:
        discounted_price = int(ORIGINAL_PRICE * (1 - DISCOUNT_PERCENT / 100))
        return {
            "is_discount": True,
            "price": discounted_price,
            "text_button": f"🔥 GONZA (BUY207) — {discounted_price:,} so'm (-10%)".replace(',', ' '),
            "display_text": f"🔥 **AKSIYA 10% FAOL!**\n💰 Asl narxi: ~{ORIGINAL_PRICE:,} so'm~\n🎉 Aksiya narxi: **{discounted_price:,} so'm**\n⏰ Aksiya 17:30 gacha davom etadi!".replace(',', ' ')
        }
    else:
        return {
            "is_discount": False,
            "price": ORIGINAL_PRICE,
            "text_button": f"🎮 GONZA (BUY207) — {ORIGINAL_PRICE:,} so'm".replace(',', ' '),
            "display_text": f"💰 Narxi: **{ORIGINAL_PRICE:,} so'm**\n💡 *Har kuni 15:30 dan 17:30 gacha 10% aksiya bo'lib o'tadi!*".replace(',', ' ')
        }

# -------------------------------------------------------------
# 2. FLASK WEB SERVER (Render.com uchun)
# -------------------------------------------------------------
app = Flask(__name__)

HTML_LAYOUT = """
<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <title>Roblox Store & Server Status</title>
    <style>
        body { font-family: sans-serif; background: #0f172a; color: white; text-align: center; padding-top: 50px; }
        .card { background: #1e293b; padding: 30px; border-radius: 12px; display: inline-block; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
        .badge { background: #22c55e; color: black; padding: 5px 12px; border-radius: 20px; font-weight: bold; }
        .promo { background: #eab308; color: black; padding: 5px 12px; border-radius: 20px; font-weight: bold; margin-top: 10px; display: inline-block; }
    </style>
</head>
<body>
    <div class="card">
        <h1>🎮 Robox Akkauntlar Do'koni</h1>
        <p>Server & Bot Holati: <span class="badge">24/7 ONLINE</span></p>
        <div class="promo">⚡ Har kuni 15:30 - 17:30 oralig'ida 10% AKSIYA!</div>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_LAYOUT)

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

# -------------------------------------------------------------
# 3. SELF-PING (Render uxlab qolmasligi uchun)
# -------------------------------------------------------------
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL", "https://saytingiz-nomi.onrender.com")

def keep_alive():
    while True:
        time.sleep(600)
        try:
            requests.get(RENDER_URL)
        except Exception:
            pass

# -------------------------------------------------------------
# 4. TELEGRAM BOT HANDLERLARI (python-telegram-bot)
# -------------------------------------------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN", "8909821057:AAHMDT9m2NsxuFiaykmWajuIsY4wDaK0tSY")

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Salom! Robox akkauntlar do'koniga xush kelibsiz!\n\n"
        "Mavjud akkauntlarni ko'rish va sotib olish uchun /buy buyrug'ini yuboring."
    )

async def cmd_buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    price_info = get_current_price_info()
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(text=price_info["text_button"], callback_data="select_buy207")]
    ])
    
    await update.message.reply_text(
        "🛒 **Mavjud Akkauntlar:**\n\n"
        "Sotib olmoqchi bo'lgan akkauntingiz ustiga bosing:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "select_buy207":
        await query.message.delete()
        price_info = get_current_price_info()
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(text="📲 Chekni yuborish (Admin)", url="https://t.me/abduraxmonova_uz")]
        ])
        
        payment_text = (
            f"✅ Siz tanladingiz: **GONZA (BUY207)**\n"
            f"{price_info['display_text']}\n\n"
            f"📌 **To'lov qilish tartibi:**\n"
            f"1. Quyidagi kartaga **{price_info['price']:,} so'm** o'tkazing:\n".replace(',', ' ') +
            f"💳 Karta raqami: `6262910225844612`\n\n"
            f"2. To'lov cheki skrinshotini @abduraxmonova_uz profiliga yuboring.\n"
            f"3. Admin to'lovni tekshirib, 2-5 daqiqa ichida login va parolni beradi!"
        )
        
        await query.message.reply_text(payment_text, reply_markup=keyboard, parse_mode="Markdown")

# -------------------------------------------------------------
# 5. MAIN
# -------------------------------------------------------------
def main():
    # Flask Server va Self-Ping'ni alohida oqimlarda ishga tushiramiz
    threading.Thread(target=run_flask, daemon=True).start()
    threading.Thread(target=keep_alive, daemon=True).start()

    # Telegram Botni ishga tushirish
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", cmd_start))
    application.add_handler(CommandHandler("buy", cmd_buy))
    application.add_handler(CommandHandler("sotibolish", cmd_buy))  # qo'shimcha so'z
    application.add_handler(CallbackQueryHandler(button_handler))

    print("[BOT]: python-telegram-bot ishga tushdi...")
    application.run_polling()

if __name__ == "__main__":
    main()
