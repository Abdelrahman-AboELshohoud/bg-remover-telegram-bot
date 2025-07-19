import logging
import os
import signal
from pathlib import Path

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from rembg_service import remove_bg
from settings import Settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)
settings = Settings()
settings.prepare_dirs()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_html(
        "Hi 👋\nSend me any <b>photo</b> or <b>image file</b> "
        "and I’ll remove the background for you."
    )


async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Download → remove background → send PNG → optional cleanup."""
    chat_id = update.effective_chat.id
    msg = await context.bot.send_message(chat_id, "⏳ Processing…")

    try:
        if update.message.photo:
            file_id = update.message.photo[-1].file_id
            file_name = f"{update.message.photo[-1].file_unique_id}.jpg"
        elif update.message.document:
            file_id = update.message.document.file_id
            file_name = update.message.document.file_name
        else:
            return

        in_path = settings.TEMP_DIR / file_name
        out_path = settings.PROCESSED_DIR / f"{Path(file_name).stem}.png"

        file = await context.bot.get_file(file_id)
        await file.download_to_drive(in_path)

        await remove_bg(in_path, out_path)

        await context.bot.send_photo(
            chat_id=chat_id,
            photo=out_path.read_bytes(),
            caption="✅ Background removed!",
        )

        if settings.CLEANUP_AFTER_SEND:
            in_path.unlink(missing_ok=True)
            out_path.unlink(missing_ok=True)

    except Exception as exc:
        logger.exception("Error while handling image")
        await context.bot.send_message(
            chat_id, "❌ Couldn’t process the image – please try another one."
        )
    finally:
        await msg.delete()


async def post_init(app: Application) -> None:
    bot = app.bot
    logger.info("Bot @%s started – ready to serve images!", bot.username)


def main() -> None:
    if not settings.TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN env var is missing!")

    app = Application.builder().token(settings.TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO | filters.Document.IMAGE, handle_image))

    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda *_: asyncio.create_task(app.stop()))

    app.run_polling()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())