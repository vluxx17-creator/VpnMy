import logging
import requests
import random
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import LabeledPrice, InlineKeyboardMarkup, InlineKeyboardButton
from keep_alive import keep_alive

# --- КОНФИГУРАЦИЯ ---
API_TOKEN = '8516621249:AAGJBXXFxUMCCfYJK_GqOYN9PMlZDIcHvHo'
PAY_TOKEN = '5339121570:TEST:38691750-ef63-4684-937c-c13d5be15bb7'
CHANNEL_ID = '@твой_канал' # Замени на свой канал (с @)
ADMIN_URL = 'https://t.me' # Для кнопки поддержки

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Запуск сервера для Render (чтобы не засыпал)
keep_alive()

SOURCES = [
    "https://githubusercontent.com",
    "https://githubusercontent.com"
]

def get_parsed_config():
    try:
        r = requests.get(random.choice(SOURCES), timeout=5)
        configs = [line for line in r.text.split('\n') if line.startswith('vless://')]
        return random.choice(configs)
    except: return None

def main_kb():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("⚡️ Подключить", callback_data="get_vpn"),
        InlineKeyboardButton("👤 Профиль", callback_data="profile")
    )
    kb.add(InlineKeyboardButton("💳 Купить подписку", callback_data="buy"))
    kb.add(
        InlineKeyboardButton("🆘 Поддержка", url=ADMIN_URL),
        InlineKeyboardButton("📢 Канал", url=f"https://t.me{CHANNEL_ID.replace('@','')}")
    )
    return kb

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    text = (f"<b>Привет в Fly VPN! 👋</b>\n\n"
            f"🚀 Лучшие VLESS протоколы для твоего интернета.\n"
            f"💎 Скорость до 1 Гбит/с.\n\n"
            f"<i>Выбери действие ниже:</i>")
    await message.answer(text, reply_markup=main_kb(), parse_mode="HTML")

@dp.callback_query_handler(text="get_vpn")
async def get_vpn(call: types.CallbackQuery):
    check = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=call.from_user.id)
    if check.status == 'left':
        await call.answer("❗️ Подпишись на канал для доступа!", show_alert=True)
        return
    
    config = get_parsed_config()
    if config:
        await call.message.answer(f"✅ <b>Твой конфиг:</b>\n\n<code>{config}</code>", parse_mode="HTML")
    else:
        await call.answer("❌ Ошибка парсера, попробуй позже", show_alert=True)

@dp.callback_query_handler(text="profile")
async def profile(call: types.CallbackQuery):
    ref_link = f"https://t.me{(await bot.get_me()).username}?start={call.from_user.id}"
    text = (f"<b>👤 Личный кабинет Fly VPN</b>\n\n"
            f"<b>ID:</b> <code>{call.from_user.id}</code>\n"
            f"<b>Статус:</b> <code>Бесплатный</code>\n\n"
            f"🔗 <b>Реф. ссылка:</b>\n<code>{ref_link}</code>")
    await call.message.edit_text(text, reply_markup=main_kb(), parse_mode="HTML")

@dp.callback_query_handler(text="buy")
async def buy(call: types.CallbackQuery):
    await bot.send_invoice(
        call.message.chat.id,
        title="Fly VPN Premium",
        description="Доступ к VIP серверам на 30 дней",
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
    kb = InlineKeyboardMarkup().add(InlineKeyboardButton("🔗 Привязать устройство", callback_data="get_vpn"))
    await message.answer("🎉 <b>Оплата прошла!</b>\nНажми кнопку для получения VIP ключа:", reply_markup=kb, parse_mode="HTML")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
