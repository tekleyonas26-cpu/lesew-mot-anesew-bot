import logging
import re
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
BOT_TOKEN = "8891300392AAE_CXCnfsc_fKvM1hsid4Wwsm_tE1UQqRo"  # ከBotFather ያገኙትን ቶከን እዚህ ይተኩ
ADMIN_CHAT_ID = ID: 8891300392  # የእርስዎን የቴሌግራም Chat ID እዚህ ይተኩ
EBOOK_FILE_PATH = "lesew_mot_anesew_mobile_ebook.pdf"
PRICE_ETB = "250"
TELEBIRR_NUMBER = "0912185298"
CBE_ACCOUNT = "1000257511538"

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
        f"1. የቴሌብር Transaction ID ወይም የክፍያ SMS መልእክቱን በጽሑፍ ይላኩ (ወዲያውኑ በራስ-ሰር ይላክልዎታል)።\n"
        f"2. ወይም የክፍያውን ደረሰኝ ስክሪንሾት (Photo) ይላኩ።"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def send_ebook(user_id: int, context: ContextTypes.DEFAULT_TYPE):
    """መጽሐፉን ለገዢው የመላኪያ ተግባር"""
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

async def handle_text_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text.strip()

    # የቴሌብር Transaction ID ፎርማት ፍተሻ (ለምሳሌ 10 ዲጂት ወይም ፊደላት የተቀላቀሉበት ከሆነ)
    # ደንበኛው የተላከውን የቴሌብር SMS ኮፒ አድርጎ ሲልክ
    if len(text) >= 6:
        await update.message.reply_text("🔄 የክፍያ ማረጋገጫ ቁጥርዎ በመረጋገጥ ላይ ነው...")
        
        # ለአድሚን ማሳወቂያ መላክ
        keyboard = [
            [
                InlineKeyboardButton("✅ አጽድቅ (Send E-Book)", callback_data=f"approve_{user.id}"),
                InlineKeyboardButton("❌ ሰርዝ (Reject)", callback_data=f"reject_{user.id}"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        admin_msg = (
            f"📥 **አዲስ የጽሑፍ/SMS ክፍያ ማረጋገጫ!**\n\n"
            f"👤 **ገዢ፦** {user.full_name} (@{user.username})\n"
            f"🆔 **User ID፦** `{user.id}`\n"
            f"💬 **የተላከው ጽሑፍ፦**\n`{text}`"
        )
        
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=admin_msg,
            reply_markup=reply_markup,
            parse_mode="Markdown",
        )
    else:
        await update.message.reply_text("⚠️ እባክዎን ትክክለኛውን የክፍያ Transaction ID ወይም የጽሑፍ ደረሰኝ ያስገቡ።")

async def handle_photo_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    photo_file_id = update.message.photo[-1].file_id

    await update.message.reply_text(
        "✅ የክፍያ ደረሰኝዎ ደርሶናል! ክፍያው እየተረጋገጠ ነው። በጥቂት ደቂቃዎች ውስጥ መጽሐፉ ይላክሎታል።"
    )

    keyboard = [
        [
            InlineKeyboardButton("✅ አጽድቅ (Send E-Book)", callback_data=f"approve_{user.id}"),
            InlineKeyboardButton("❌ ሰርዝ (Reject)", callback_data=f"reject_{user.id}"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    admin_msg = (
        f"📥 **አዲስ የፎቶ/ስክሪንሾት ደረሰኝ ደርሷል!**\n\n"
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
        try:
            await send_ebook(user_id, context)
            if query.message.photo:
                await query.edit_message_caption(
                    caption=f"{query.message.caption}\n\n✅ **ተጸድቋል - መጽሐፉ ተልኳል!**"
                )
            else:
                await query.edit_message_text(
                    text=f"{query.message.text}\n\n✅ **ተጸድቋል - መጽሐፉ ተልኳል!**"
                )
        except Exception as e:
            await query.message.reply_text(f"⚠️ ፋይሉን በመላክ ላይ ስህተት ተፈጥሯል፦ {e}")

    elif action == "reject":
        await context.bot.send_message(
            chat_id=user_id,
            text="⚠️ የላኩት የክፍያ ደረሰኝ አልተረጋገጠም። እባክዎን ትክክለኛውን ደረሰኝ እንደገና ይላኩ ወይም የአገልግሎት መስመራችንን ያናግሩ።",
        )
        if query.message.photo:
            await query.edit_message_caption(caption=f"{query.message.caption}\n\n❌ **ውድቅ ተደርጓል!**")
        else:
            await query.edit_message_text(text=f"{query.message.text}\n\n❌ **ውድቅ ተደርጓል!**")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_receipt))   
ا   app.add_handler(MessageHandler(filters.PHOTO, handle_photo_receipt))
    app.add_handler(CallbackQueryHandler(button_callback))

    print("🤖 ቦቱ በስኬት ስራ ጀምሯል...")
    app.run_polling()

if __name__ == "__main__":
    main()
                               //////////////////////////////////////////////


      import logging
import re
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
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # ከBotFather ያገኙትን ቶከን እዚህ ይተኩ
ADMIN_CHAT_ID = 123456789  # የእርስዎን የቴሌግራም Chat ID እዚህ ይተኩ
EBOOK_FILE_PATH = "lesew_mot_anesew_mobile_ebook.pdf"
PRICE_ETB = "250"
TELEBIRR_NUMBER = "0912185298"
CBE_ACCOUNT = "1000257511538"

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
        f"1. የቴሌብር Transaction ID ወይም የክፍያ SMS መልእክቱን በጽሑፍ ይላኩ (ወዲያውኑ በራስ-ሰር ይላክልዎታል)።\n"
        f"2. ወይም የክፍያውን ደረሰኝ ስክሪንሾት (Photo) ይላኩ።"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def send_ebook(user_id: int, context: ContextTypes.DEFAULT_TYPE):
    """መጽሐፉን ለገዢው የመላኪያ ተግባር"""
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

async def handle_text_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text.strip()

    # የቴሌብር Transaction ID ፎርማት ፍተሻ (ለምሳሌ 10 ዲጂት ወይም ፊደላት የተቀላቀሉበት ከሆነ)
    # ደንበኛው የተላከውን የቴሌብር SMS ኮፒ አድርጎ ሲልክ
    if len(text) >= 6:
        await update.message.reply_text("🔄 የክፍያ ማረጋገጫ ቁጥርዎ በመረጋገጥ ላይ ነው...")
        
        # ለአድሚን ማሳወቂያ መላክ
        keyboard = [
            [
                InlineKeyboardButton("✅ አጽድቅ (Send E-Book)", callback_data=f"approve_{user.id}"),
                InlineKeyboardButton("❌ ሰርዝ (Reject)", callback_data=f"reject_{user.id}"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        admin_msg = (
            f"📥 **አዲስ የጽሑፍ/SMS ክፍያ ማረጋገጫ!**\n\n"
            f"👤 **ገዢ፦** {user.full_name} (@{user.username})\n"
            f"🆔 **User ID፦** `{user.id}`\n"
            f"💬 **የተላከው ጽሑፍ፦**\n`{text}`"
        )
        
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=admin_msg,
            reply_markup=reply_markup,
            parse_mode="Markdown",
        )
    else:
        await update.message.reply_text("⚠️ እባክዎን ትክክለኛውን የክፍያ Transaction ID ወይም የጽሑፍ ደረሰኝ ያስገቡ።")

async def handle_photo_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    photo_file_id = update.message.photo[-1].file_id

    await update.message.reply_text(
        "✅ የክፍያ ደረሰኝዎ ደርሶናል! ክፍያው እየተረጋገጠ ነው። በጥቂት ደቂቃዎች ውስጥ መጽሐፉ ይላክሎታል።"
    )

    keyboard = [
        [
            InlineKeyboardButton("✅ አጽድቅ (Send E-Book)", callback_data=f"approve_{user.id}"),
            InlineKeyboardButton("❌ ሰርዝ (Reject)", callback_data=f"reject_{user.id}"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    admin_msg = (
        f"📥 **አዲስ የፎቶ/ስክሪንሾት ደረሰኝ ደርሷል!**\n\n"
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
        try:
            await send_ebook(user_id, context)
            if query.message.photo:
                await query.edit_message_caption(
                    caption=f"{query.message.caption}\n\n✅ **ተጸድቋል - መጽሐፉ ተልኳል!**"
                )
            else:
                await query.edit_message_text(
                    text=f"{query.message.text}\n\n✅ **ተጸድቋል - መጽሐፉ ተልኳል!**"
                )
        except Exception as e:
            await query.message.reply_text(f"⚠️ ፋይሉን በመላክ ላይ ስህተት ተፈጥሯል፦ {e}")

    elif action == "reject":
        await context.bot.send_message(
            chat_id=user_id,
            text="⚠️ የላኩት የክፍያ ደረሰኝ አልተረጋገጠም። እባክዎን ትክክለኛውን ደረሰኝ እንደገና ይላኩ ወይም የአገልግሎት መስመራችንን ያናግሩ።",
        )
        if query.message.photo:
            await query.edit_message_caption(caption=f"{query.message.caption}\n\n❌ **ውድቅ ተደርጓል!**")
        else:
            await query.edit_message_text(text=f"{query.message.text}\n\n❌ **ውድቅ ተደርጓል!**")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_receipt))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo_receipt))
    app.add_handler(CallbackQueryHandler(button_callback))

    print("🤖 ቦቱ በስኬት ስራ ጀምሯል...")
    app.run_polling()

if __name__ == "__main__":
    main()
python-telegram-bot>=20.0



