import logging
import requests
import random
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import LabeledPrice, InlineKeyboardMarkup, InlineKeyboardButton
from keep_alive import keep_alive

# --- КОНФИГУРАЦИЯ ---
API_TOKEN = '8516621249:AAGJBXXFxUMCCfYJK_GqOYN9PMlZDIcHvHo'
PAY_TOKEN = '5339121570:TEST:38691750-ef63-4684-937c-c13d5be15bb7'
ADMIN_URL = 'https://t.me'  # Контакт саппорта

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Запуск Flask-сервера для Render
keep_alive()

# Базы бесплатных VLESS конфигураций
SOURCES = [
    "https://githubusercontent.com",
    "https://githubusercontent.com",
    "https://githubusercontent.com"
]

def get_parsed_config():
    """Бот скачивает ключи из открытых репозиториев"""
    random.shuffle(SOURCES)
    for source in SOURCES:
        try:
            r = requests.get(source, timeout=10)
            if r.status_code == 200:
                # Фильтруем только vless и убираем лишние пробелы
                configs = [l.strip() for l in r.text.split('\n') if l.strip().startswith('vless://')]
                if configs:
                    return random.choice(configs)
        except Exception as e:
            logging.error(f"Ошибка источника {source}: {e}")
            continue
    return None

def main_kb():
    """Главное меню в стиле Fly VPN"""
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("⚡️ Подключить VPN", callback_data="get_vpn"),
        InlineKeyboardButton("👤 Профиль", callback_data="profile")
    )
    kb.add(InlineKeyboardButton("💳 Купить VIP подписку", callback_data="buy"))
    kb.add(
        InlineKeyboardButton("🆘 Поддержка", url=ADMIN_URL),
        InlineKeyboardButton("📢 Наш канал", url="https://t.me")
    )
    return kb

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    text = (f"<b>Fly VPN @tgxel</b> 👋\n\n"
            f"🚀 Автоматический поиск и выдача VLESS ключей.\n"
            f"💎 VIP доступ — это максимальная скорость без очереди.\n\n"
            f"<i>Нажми кнопку ниже, чтобы получить доступ:</i>")
    await message.answer(text, reply_markup=main_kb(), parse_mode="HTML")

@dp.callback_query_handler(text="get_vpn")
async def get_vpn(call: types.CallbackQuery):
    # Показываем юзеру, что бот ищет сервер
    await call.answer("🔍 Ищу свободный сервер...")
    
    config = get_parsed_config()
    if config:
        # Экранируем спецсимволы в конфиге для безопасности HTML
        clean_config = config.replace('<', '&lt;').replace('>', '&gt;')
        msg = (f"✅ <b>Fly VPN подключен!</b>\n\n"
               f"<code>{clean_config}</code>\n\n"
               f"👆 <b>Нажми на код</b>, чтобы скопировать его.\n"
               f"Инструкция: Открой <b>Happ</b> -> Нажми '+' -> 'Import from Clipboard'.")
        await call.message.answer(msg, parse_mode="HTML")
    else:
        await call.message.answer("⚠️ Все бесплатные сервера сейчас перегружены. Попробуй через пару минут или воспользуйся VIP.")

@dp.callback_query_handler(text="profile")
async def profile(call: types.CallbackQuery):
    bot_info = await bot.get_me()
    ref_link = f"https://t.me{bot_info.username}?start={call.from_user.id}"
    text = (f"<b>👤 Личный кабинет</b>\n\n"
            f"<b>Ваш ID:</b> <code>{call.from_user.id}</code>\n"
            f"<b>Тариф:</b> <code>Бесплатный</code>\n\n"
            f"🔗 <b>Ваша ссылка для друзей:</b>\n<code>{ref_link}</code>\n\n"
            f"<i>За каждого приглашенного скоро будут бонусы!</i>")
    await call.message.edit_text(text, reply_markup=main_kb(), parse_mode="HTML")

@dp.callback_query_handler(text="buy")
async def buy(call: types.CallbackQuery):
    try:
        await bot.send_invoice(
            call.message.chat.id,
            title="Fly VPN Premium (30 дней)",
            description="Доступ к приватным скоростным серверам",
            provider_token=PAY_TOKEN,
            currency="RUB",
            prices=[LabeledPrice(label="VIP доступ", amount=19900)], # 199.00 руб
            start_parameter="fly-vpn-premium",
            payload="vip_sub_payload"
        )
    except Exception as e:
        logging.error(f"Ошибка счета: {e}")
        await call.answer("❌ Ошибка платежной системы. Обратитесь в поддержку.", show_alert=True)

@dp.pre_checkout_query_handler(lambda q: True)
async def checkout(q: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(q.id, ok=True)

@dp.message_handler(content_types=types.ContentType.SUCCESSFUL_PAYMENT)
async def success(message: types.Message):
    await message.answer("🎉 <b>Оплата прошла успешно!</b>\n\nТеперь вы VIP-клиент. Ваши сервера Fly VPN будут работать на максимальной скорости.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
