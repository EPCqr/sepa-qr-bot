import qrcode
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from io import BytesIO
import os


TOKEN = os.getenv("THETOKEN")

if not TOKEN:
    raise Exception("TOKEN is missing! Set it in Railway Variables.")

def build_epc_qr(iban, name, amount, reference):
    amount_str = f"EUR{float(amount):.2f}"

    epc = "\n".join([
        "BCD",
        "001",
        "1",
        "SCT",
        "",             # BIC optional
        name,
        iban,
        amount_str,
        "",             # purpose optional
        reference
    ])
    return epc

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Send payment data like:\nIBAN;Name;Amount;Reference\n\nExample:\nNL91ABNA0417164300;John Doe;10.50;Invoice123"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = update.message.text.split(";")
        iban, name, amount, reference = data

        epc_string = build_epc_qr(iban, name, amount, reference)

        qr = qrcode.make(epc_string)
        bio = BytesIO()
        bio.name = "payment.png"
        qr.save(bio, "PNG")
        bio.seek(0)

        await update.message.reply_photo(photo=bio)

    except Exception as e:
        await update.message.reply_text("Invalid format. Use:\nIBAN;Name;Amount;Reference")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling()
