import logging
import random
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import LabeledPrice, InlineKeyboardMarkup, InlineKeyboardButton
from keep_alive import keep_alive

# --- НАСТРОЙКИ ---
API_TOKEN = '8516621249:AAGJBXXFxUMCCfYJK_GqOYN9PMlZDIcHvHo'
PAY_TOKEN = '5339121570:TEST:38691750-ef63-4684-937c-c13d5be15bb7'
ADMIN_URL = 'https://t.me/ovnoy'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

keep_alive()

# Временная база данных в оперативной памяти (сбросится при перезагрузке)
# В идеале здесь нужен файл или БД, но для 0 бюджета работаем так:
users_db = {} 

MY_KEYS = [
    "ss://Y2hhY2hhMjAtaWV0Zi1wb2x5MTMwNTpBUmd2R1p5d0ErZ2FjZ0dWMjZCdm11MDUrd1ptUlcvaitBZFUrWjhCdDQ0PQ==@79.127.200.169:990#%F0%9F%87%A8%F0%9F%87%A6CA-79.127.200.169-0192",
    "vless://d342d11e-d424-4583-b36e-524ab1f0afa4@162.159.36.5:2083?allowInsecure=1&encryption=none&host=newwk1.f1w.de5.net&path=%2F&security=tls&sni=newwk1.f1w.de5.net&type=ws#%3E%3E%40oneclickvpnkeys%3A%3AUS"
    "vless://14c80e0e-f7ce-4991-94fc-99a1db4a9b1e@159.89.87.21:28190?encryption=none&flow=xtls-rprx-vision&fp=chrome&pbk=ZJRnFU-1s1JOnO8E9uZ7b00l1fPEh63fGRbdBANFRno&security=reality&sni=aws.amazon.com&type=tcp#%3E%3E%40oneclickvpnkeys%3A%3AUS"
]

def main_kb():
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
    user_id = message.from_user.id
    if user_id not in users_db:
        users_db[user_id] = {'status': 'new', 'expire': None}
    
    text = (f"<b>Fly VPN @tgxel</b> 👋\n\n"
            f"🎁 Тебе доступен бесплатный тест на 7 дней!\n"
            f"🚀 Жми кнопку ниже, чтобы получить свой VLESS ключ.")
    await message.answer(text, reply_markup=main_kb(), parse_mode="HTML")

@dp.callback_query_handler(text="get_vpn")
async def get_vpn(call: types.CallbackQuery):
    user_id = call.from_user.id
    user = users_db.get(user_id, {'status': 'new', 'expire': None})

    # Логика бесплатного периода (7 дней)
    if user['status'] == 'new':
        user['status'] = 'trial'
        user['expire'] = datetime.now() + timedelta(days=7)
        users_db[user_id] = user
    
    # Проверка срока годности
    if user['status'] == 'trial' and datetime.now() > user['expire']:
        await call.message.answer("❌ <b>Твой пробный период (7 дней) закончился.</b>\nПожалуйста, купи Premium для продолжения.", parse_mode="HTML")
        return

    config = random.choice(MY_KEYS)
    clean_config = config.replace('<', '&lt;').replace('>', '&gt;')
    msg = (f"✅ <b>Доступ активен!</b>\n\n"
           f"<code>{clean_config}</code>\n\n"
           f"👆 <b>Нажми на код</b>, чтобы скопировать.")
    await call.message.answer(msg, parse_mode="HTML")

@dp.callback_query_handler(text="profile")
async def profile(call: types.CallbackQuery):
    user = users_db.get(call.from_user.id, {'status': 'Бесплатный', 'expire': 'Нет'})
    status = "Premium 💎" if user['status'] == 'premium' else "Пробный (7 дней) 🎁"
    expire = user['expire'].strftime("%d.%m.%Y") if user['expire'] else "Не начат"
    
    text = (f"<b>👤 Личный кабинет</b>\n\n"
            f"<b>Ваш ID:</b> <code>{call.from_user.id}</code>\n"
            f"<b>Статус:</b> <code>{status}</code>\n"
            f"<b>Действует до:</b> <code>{expire}</code>")
    await call.message.edit_text(text, reply_markup=main_kb(), parse_mode="HTML")

@dp.callback_query_handler(text="buy")
async def buy(call: types.CallbackQuery):
    await bot.send_invoice(
        call.message.chat.id,
        title="Fly VPN Premium (30 дней)",
        description="Максимальная скорость + поддержка 24/7",
        provider_token=PAY_TOKEN,
        currency="RUB",
        prices=[LabeledPrice(label="VIP доступ", amount=19900)],
        payload="vip_sub",
        start_parameter="pay"
    )

@dp.pre_checkout_query_handler(lambda q: True)
async def checkout(q: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(q.id, ok=True)

@dp.message_handler(content_types=types.ContentType.SUCCESSFUL_PAYMENT)
async def success(message: types.Message):
    # Обновляем статус пользователя на Premium
    users_db[message.from_user.id] = {
        'status': 'premium', 
        'expire': datetime.now() + timedelta(days=30)
    }
    await message.answer("🎉 <b>Оплата прошла!</b>\nТеперь у тебя Premium доступ на 30 дней. Приятного пользования!")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
