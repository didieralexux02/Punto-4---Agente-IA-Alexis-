"""
ACH Funding Agent - Telegram Bot
Fintech Technical Assessment
"""

import os
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from agent_ import ACHAgent

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# In-memory session store: {chat_id: ACHAgent instance}
sessions: dict[int, ACHAgent] = {}


def get_or_create_agent(chat_id: int) -> ACHAgent:
    if chat_id not in sessions:
        sessions[chat_id] = ACHAgent()
    return sessions[chat_id]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    sessions[chat_id] = ACHAgent()  # Fresh session on /start
    agent = sessions[chat_id]
    welcome = agent.get_welcome_message()
    await update.message.reply_text(welcome)


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    sessions[chat_id] = ACHAgent()
    await update.message.reply_text(
        "🔄 Sesión reiniciada. Escribe /start para comenzar de nuevo."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    user_text = update.message.text.strip()

    agent = get_or_create_agent(chat_id)
    response = agent.process_message(user_text)
    await update.message.reply_text(response, parse_mode="Markdown")


def main() -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set")

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("ACH Agent Bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
