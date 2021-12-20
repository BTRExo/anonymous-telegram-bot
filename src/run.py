import emoji
from loguru import logger

from src.bot import bot
from src.constants import keyboards
from src.filters import IsAdmin


def admin_of_group(message):
	bot.send_message(message.chat.id, 'You are admin of this group!')
class Bot():
    """
    Template for Telegram Bot.
    """
    def __init__(self, telebot):
        self.bot = telebot

        # register handlers
        self.handlers()

        # add custom filters
        self.bot.add_custom_filter(IsAdmin())

    def handlers(self):
        @self.bot.message_handler(is_admin=True)
        def admin_of_group(message):
            self.send_message(message.chat.id, 'You are admin of this group!')

        @self.bot.message_handler(func=lambda m: True)
        def echo_all(message):
            self.send_message(
                message.chat.id, "Choose one option:",
                reply_markup=keyboards.main
            )

    def run(self):
        logger.info('Bot is running...')
        self.bot.infinity_polling()

    def send_message(self, chat_id, text, reply_markup=None, emojize=True):
        """
        send message for telegram bot.
        """
        if emojize:
            text = emoji.emojize(text, use_aliases=True)

        self.bot.send_message(chat_id, text, reply_markup=reply_markup)

if __name__ == '__main__':
    logger.info('Bot Started!')
    tlgrmbot = Bot(telebot=bot)
    tlgrmbot.run()
