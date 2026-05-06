import logging
import requests
import random
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import LabeledPrice, InlineKeyboardMarkup, InlineKeyboardButton
from keep_alive import keep_alive

# --- НАСТРОЙКИ ---
API_TOKEN = '8516621249:AAGJBXXFxUMCCfYJK_GqOYN9PMlZDIcHvHo'
PAY_TOKEN = '5339121570:TEST:38691750-ef63-4684-937c-c13d5be15bb7'
ADMIN_URL = 'https://t.me' # Контакт для саппорта

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Источники VLESS
SOURCES = [
    "https://githubusercontent.com",
    "https://githubusercontent.com",
    "https://githubusercontent.com"
]

def get_parsed_config():
    """Бот сам заходит на GitHub и берет ссылку"""
    random.shuffle(SOURCES) # Перемешиваем источники для надежности
    for source in SOURCES:
        try:
            r = requests.get(source, timeout=10)
            configs = [l.strip() for l in r.text.split('\n') if l.startswith('vless://')]
            if configs:
                return random.choice(configs)
        except:
            continue
    return None

def main_kb():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("⚡️ Подключить VPN", callback_data="get_vpn"),
        InlineKeyboardButton("👤 Профиль", callback_data="profile")
    )
    kb.add(InlineKeyboardButton("💳 Купить VIP", callback_data="buy"))
    kb.add(
        InlineKeyboardButton("🆘 Поддержка", url=ADMIN_URL),
        InlineKeyboardButton("📢 Наш канал", url="https://t.me")
    )
    return kb

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    text = (f"<b>Fly VPN @tgxel</b> 👋\n\n"
            f"🚀 Жми на кнопку ниже, чтобы получить свежий VLESS ключ.\n"
            f"💎 VIP доступ даст еще больше скорости.\n\n"
            f"<i>Бот работает полностью автоматически!</i>")
    await message.answer(text, reply_markup=main_kb(), parse_mode="HTML")

@dp.callback_query_handler(text="get_vpn")
async def get_vpn(call: types.CallbackQuery):
    await call.answer("🔍 Поиск свободного сервера...") # Показываем уведомление
    
    config = get_parsed_config()
    if config:
        msg = (f"✅ <b>Fly VPN подключен!</b>\n\n"
               f"<code>{config}</code>\n\n"
               f"👆 <b>Нажми на код</b>, чтобы скопировать.\n"
               f"Открой <b>Happ</b>, нажми '+' и выбери 'Import from Clipboard'.")
        await call.message.answer(msg, parse_mode="HTML")
    else:
        await call.message.answer("⚠️ Все бесплатные сервера сейчас заняты. Попробуй через минуту или купи VIP.")

@dp.callback_query_handler(text="profile")
async def profile(call: types.CallbackQuery):
    bot_info = await bot.get_me()
    ref = f"https://t.me{bot_info.username}?start={call.from_user.id}"
    text = (f"👤 <b>Личный кабинет</b>\n\n"
            f"<b>Ваш ID:</b> <code>{call.from_user.id}</code>\n"
            f"<b>Статус:</b> <code>Бесплатный</code>\n\n"
            f"🔗 <b>Реф. ссылка:</b>\n<code>{ref}</code>")
    await call.message.edit_text(text, reply_markup=main_kb(), parse_mode="HTML")

@dp.callback_query_handler(text="buy")
async def buy(call: types.CallbackQuery):
    try:
        await bot.send_invoice(
            call.message.chat.id,
            title="Fly VPN VIP",
            description="Доступ к приватным серверам на 30 дней",
            provider_token=PAY_TOKEN,
            currency="RUB",
            prices=[LabeledPrice(label="VIP доступ", amount=19900)],
            payload="vip_sub"
        )
    except Exception as e:
        await call.answer("❌ Ошибка оплаты. Проверь настройки токена.", show_alert=True)

@dp.pre_checkout_query_handler(lambda q: True)
async def checkout(q: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(q.id, ok=True)

@dp.message_handler(content_types=types.ContentType.SUCCESSFUL_PAYMENT)
async def success(message: types.Message):
    await message.answer("🎉 <b>Оплата прошла!</b> Теперь ты VIP. Нажми 'Подключить' для получения быстрого сервера.")

if __name__ == '__main__':
    keep_alive()
    executor.start_polling(dp, skip_updates=True)
