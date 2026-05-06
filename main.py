import logging
import requests
import random
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import LabeledPrice, InlineKeyboardMarkup, InlineKeyboardButton
from keep_alive import keep_alive

# --- НАСТРОЙКИ ---
API_TOKEN = '8516621249:AAGJBXXFxUMCCfYJK_GqOYN9PMlZDIcHvHo'
PAY_TOKEN = '5339121570:TEST:38691750-ef63-4684-937c-c13d5be15bb7'
CHANNEL_ID = '@tgxel'  # Твой канал
ADMIN_URL = 'https://t.me' # Замени на свой контакт для саппорта

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Источники бесплатных VLESS
SOURCES = [
    "https://githubusercontent.com",
    "https://githubusercontent.com"
]

def get_parsed_config():
    try:
        r = requests.get(random.choice(SOURCES), timeout=5)
        configs = [l.strip() for l in r.text.split('\n') if l.startswith('vless://')]
        return random.choice(configs) if configs else None
    except: return None

def main_kb():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("⚡️ Подключить VPN", callback_data="get_vpn"),
        InlineKeyboardButton("👤 Профиль", callback_data="profile")
    )
    kb.add(InlineKeyboardButton("💳 Купить подписку", callback_data="buy"))
    kb.add(
        InlineKeyboardButton("🆘 Поддержка", url=ADMIN_URL),
        InlineKeyboardButton("📢 Канал", url="https://t.me")
    )
    return kb

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    text = (f"<b>Привет в Fly VPN! 👋</b>\n\n"
            f"🚀 Лучшие VLESS сервера от канала @tgxel.\n"
            f"⚡️ Скорость без ограничений.\n\n"
            f"<i>Для работы используй меню:</i>")
    await message.answer(text, reply_markup=main_kb(), parse_mode="HTML")

@dp.callback_query_handler(text="get_vpn")
async def get_vpn(call: types.CallbackQuery):
    # Проверка подписки на @tgxel
    check = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=call.from_user.id)
    if check.status == 'left':
        await call.answer("❗️ Сначала подпишись на @tgxel", show_alert=True)
        return

    config = get_parsed_config()
    if config:
        msg = (f"✅ <b>Твой конфиг готов:</b>\n\n"
               f"<code>{config}</code>\n\n"
               f"👆 Нажми, чтобы скопировать. Вставь в Happ.")
        await call.message.answer(msg, parse_mode="HTML")
    else:
        await call.answer("❌ Ошибка базы, попробуй позже", show_alert=True)

@dp.callback_query_handler(text="profile")
async def profile(call: types.CallbackQuery):
    bot_info = await bot.get_me()
    ref = f"https://t.me{bot_info.username}?start={call.from_user.id}"
    text = (f"<b>👤 Личный кабинет</b>\n\n"
            f"<b>ID:</b> <code>{call.from_user.id}</code>\n"
            f"<b>Подписка:</b> @tgxel\n\n"
            f"🔗 <b>Реф. ссылка:</b>\n<code>{ref}</code>")
    await call.message.edit_text(text, reply_markup=main_kb(), parse_mode="HTML")

@dp.callback_query_handler(text="buy")
async def buy(call: types.CallbackQuery):
    await bot.send_invoice(
        call.message.chat.id,
        title="Fly VPN Premium",
        description="VIP доступ на 30 дней",
        provider_token=PAY_TOKEN,
        currency="RUB",
        prices=[LabeledPrice(label="Premium", amount=19900)],
        payload="vip"
    )

@dp.pre_checkout_query_handler(lambda q: True)
async def checkout(q: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(q.id, ok=True)

@dp.message_handler(content_types=types.ContentType.SUCCESSFUL_PAYMENT)
async def success(message: types.Message):
    await message.answer("🎉 <b>Оплата принята!</b>\nИспользуй кнопку 'Подключить' для VIP ключа.")

if __name__ == '__main__':
    keep_alive()
    executor.start_polling(dp, skip_updates=True)
