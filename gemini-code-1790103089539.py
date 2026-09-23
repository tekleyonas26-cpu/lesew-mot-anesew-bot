import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# ----------------- Configuration -----------------
BOT_TOKEN = "የእርስዎ_BOT_TOKEN_እዚህ ይግቡ"
ADMIN_CHAT_ID = 123456789  # የእርስዎ Telegram Chat ID (አድሚን)
EBOOK_FILE_PATH = "lesew_mot_anesew_mobile_ebook.pdf"
PRICE_ETB = "250"  # የመጽሐፉ ዋጋ
TELEBIRR_NUMBER = "09XXXXXXXX"  # የቴሌብር ቁጥርዎ
CBE_ACCOUNT = "1000XXXXXXXXX"  # የንግድ ባንክ ሂሳብ ቁጥርዎ
# -------------------------------------------------

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        f"📖 **«ለሰው ሞት አነሰው»** - ደራሲ ዮናስ ተክሌ\n\n"
        f"እንኳን ወደ ህልውናዊና ፍልስፍናዊው መጽሐፍ መግዣ ቦት በደህና መጡ! \n\n"
        f"💰 **የመጽሐፉ ዋጋ፦** {PRICE_ETB} ብር\n\n"
        f"💳 **የክፍያ አማራጮች፦**\n"
        f"• **Telebirr:** `{TELEBIRR_NUMBER}`\n"
        f"• **CBE (ንግድ ባንክ):** `{CBE_ACCOUNT}`\n\n"
        f"📌 **ክፍያ ከፈጸሙ በኋላ፦**\n"
        f"የክፍያውን ደረሰኝ/ስክሪንሾት (Receipt Photo) በዚህ ቦት ያያይዙና ይላኩ። "
        f"ክፍያው እንደተረጋገጠ መጽሐፉ በራስ-ሰር ይላክሎታል።"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def handle_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    photo_file_id = update.message.photo[-1].file_id

    # ለደንበኛው ማረጋገጫ መስጠት
    await update.message.reply_text(
        "✅ የክፍያ ደረሰኝዎ ደርሶናል! ክፍያው እየተረጋገጠ ነው። በጥቂት ደቂቃዎች ውስጥ መጽሐፉ ይላክሎታል።"
    )

    # ለአድሚን ደረሰኙን መላክ (የማጽደቂያ ቁልፎችን ጨምሮ)
    keyboard = [
        [
            InlineKeyboardButton(
                "✅ አጽድቅ (Send E-Book)", callback_data=f"approve_{user.id}"
            ),
            InlineKeyboardButton(
                "❌ ሰርዝ (Reject)", callback_data=f"reject_{user.id}"
            ),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    admin_msg = (
        f"📥 **አዲስ የኢ-ቡክ ትዕዛዝ ደርሷል!**\n\n"
        f"👤 **ገዢ፦** {user.full_name} (@{user.username})\n"
        f"🆔 **User ID፦** `{user.id}`"
    )

    await context.bot.send_photo(
        chat_id=ADMIN_CHAT_ID,
        photo=photo_file_id,
        caption=admin_msg,
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data.split("_")
    action = data[0]
    user_id = int(data[1])

    if action == "approve":
        # ደንበኛው ጋር መጽሐፉን በራስ-ሰር መላክ
        try:
            with open(EBOOK_FILE_PATH, "rb") as book_file:
                await context.bot.send_document(
                    chat_id=user_id,
                    document=book_file,
                    caption=(
                        "🎉 **ክፍያዎ ተረጋግጧል!**\n\n"
                        "«ለሰው ሞት አነሰው» የተሰኘውን የኢ-ቡክ PDF ፋይል ከዚህ ማውረድ ይችላሉ። መልካም ንባብ!"
                    ),
                    parse_mode="Markdown",
                )
            await query.edit_message_caption(
                caption=f"{query.message.caption}\n\n✅ **ተጸድቋል - መጽሐፉ ለገዢው ተልኳል!**"
            )
        except Exception as e:
            await query.message.reply_text(f"⚠️ ፋይሉን በመላክ ላይ ስህተት ተፈጥሯል፦ {e}")

    elif action == "reject":
        # ለደንበኛው የክፍያ አለመቀበል መልእክት መላክ
        await context.bot.send_message(
            chat_id=user_id,
            text="⚠️ የላኩት የክፍያ ደረሰኝ አልተረጋገጠም። እባክዎን ትክክለኛውን ደረሰኝ እንደገና ይላኩ ወይም የአገልግሎት መስመራችንን ያናግሩ።",
        )
        await query.edit_message_caption(
            caption=f"{query.message.caption}\n\n❌ **ውድቅ ተደርጓል!**"
        )

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_receipt))
    app.add_handler(CallbackQueryHandler(button_callback))

    print("🤖 ቦቱ በስኬት ስራ ጀምሯል...")
    app.run_polling()

if __name__ == "__main__":
    main()