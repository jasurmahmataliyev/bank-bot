from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from db import check_login, check_phone_number, add_user, read_excel_data

# Hardcode ma'lumotlarni qo'shish
add_user('admin', 'admin123', '+998904110135')
add_user('aaaa', 'aaaa1', '+998975300005')

# Conversation states
USERNAME, PASSWORD, PHONE_NUMBER, WEB_APP_OPENED = range(4)

def normalize_phone_number(phone_number: str) -> str:
    """
    Telefon raqamni normalizatsiya qiladi: '+998' prefiksni qo'shadi agar kerak bo'lsa.
    """
    phone_number = phone_number.strip().replace(" ", "")
    
    # Agar raqam '+' bilan boshlanmasa, uni to'g'ri formatga keltiramiz
    if not phone_number.startswith('+'):
        if phone_number.startswith('998'):
            phone_number = '+' + phone_number
        elif phone_number.startswith('9'):
            phone_number = '+998' + phone_number[1:]
        elif phone_number.startswith('0'):
            phone_number = '+998' + phone_number[1:]

    return phone_number

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Loginni kiriting:")
    return USERNAME

async def username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['username'] = update.message.text
    await update.message.reply_text("Parolni kiriting:")
    return PASSWORD

async def password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = context.user_data['username']
    password = update.message.text

    if check_login(username, password):
        # Foydalanuvchi login va parolni to'g'ri kiritsa, avvalgi xabarini o'chirish
        await update.message.delete()

        # Telefon raqamini yuborish tugmasini ko'rsatish
        button = KeyboardButton("Telefon raqamni yuborish", request_contact=True)
        reply_markup = ReplyKeyboardMarkup([[button]], resize_keyboard=True)
        await update.message.reply_text("Telefon raqamingizni yuboring:", reply_markup=reply_markup)
        return PHONE_NUMBER
    else:
        await update.message.reply_text("Login yoki parol noto'g'ri. Qaytadan urinib ko'ring.")
        return USERNAME

async def phone_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = context.user_data['username']
    phone_number = update.message.contact.phone_number
    normalized_phone_number = normalize_phone_number(phone_number)

    if check_phone_number(username, normalized_phone_number):
        context.user_data['logged_in'] = True

        # Web ilovani ochish tugmasi
        keyboard = [
            [InlineKeyboardButton("Botdan to'liq foydalanishingiz mumkin", web_app={"url": "https://web-site-aloqa-bank.vercel.app/"})]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Tugmani yuborish va xabar ID'sini saqlash
        sent_message = await update.message.reply_text("Tasdiqlandi! Botdan to'liq foydalanishingiz mumkin:", reply_markup=reply_markup)
        context.user_data['web_app_message_id'] = sent_message.message_id

        # Web ilovaga kirgandan keyin xabarni o'chirish uchun holatni o'rnatish
        return WEB_APP_OPENED
    else:
        await update.message.reply_text("Telefon raqami noto'g'ri. Qaytadan urinib ko'ring.")
        return PHONE_NUMBER

async def web_app_opened(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id

    # Xabarni o'chirish
    if 'web_app_message_id' in context.user_data:
        await context.bot.delete_message(chat_id=chat_id, message_id=context.user_data['web_app_message_id'])
        del context.user_data['web_app_message_id']

    # Excel ma'lumotlarini o'qish
    excel_data = read_excel_data('data.xlsx')  # data.xlsx fayl nomi

    # Excel ma'lumotlarini foydalanuvchiga ko'rsatish
    # Bu yerda ma'lumotlarni qanday ko'rsatishni belgilash
    # Masalan, biror qismini foydalanuvchiga yuborish:
    await update.message.reply_text("Excel ma'lumotlari: \n" + excel_data.head().to_string())

    # Foydalanuvchiga qayta autentifikatsiya qilishni so'rash
    await update.message.reply_text("Login, parol va telefon raqamini qayta kiriting. "
                                    "Shundan so'ng yana ilovadan foydalana olasiz.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bekor qilindi.")
    return ConversationHandler.END

if __name__ == '__main__':
    TOKEN = "7504992702:AAFFyhbyfSn-hE9QkQSNKSPM4Qr8nVQP8v8"  # Tokenni o'zgartiring

    app = ApplicationBuilder().token(TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, username)],
            PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, password)],
            PHONE_NUMBER: [MessageHandler(filters.CONTACT, phone_number)],
            WEB_APP_OPENED: [MessageHandler(filters.TEXT & ~filters.COMMAND, web_app_opened)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    app.add_handler(conv_handler)

    print("Bot ishlamoqda...")
    app.run_polling()





# 7504992702:AAFFyhbyfSn-hE9QkQSNKSPM4Qr8nVQP8v8