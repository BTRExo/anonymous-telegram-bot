import emoji
from loguru import logger

from src.bot import bot
from src.constants import keyboards, keys, states
from src.db import mongodb
from src.filters import IsAdmin


class Bot():
    """
    Telegram Bot to connect two strangers.
    """
    def __init__(self, telebot, db):
        self.bot = telebot

        # register handlers
        self.handlers()

        # add custom filters
        self.bot.add_custom_filter(IsAdmin())

        # database
        self.users = db.users

    def handlers(self):
        @self.bot.message_handler(commands=['start'])
        def start(message):
            self.send_message(
                 message.chat.id,
                f'Hey, welcome <strong>{message.chat.first_name}</strong>!',
                reply_markup=keyboards.main
                )
            # log user data in db
            self.users.update_one(
                {'chat.id': message.chat.id},
                {'$set': message.json},
                upsert=True
                )
            self.update_state(message.chat.id, states.main)

        @self.bot.message_handler(regexp = emoji.emojize(keys.random_connect))
        def random_connect(message):
            self.send_message(
                 message.chat.id,
                'Connecting to a random stranger... :busts_in_silhouette:',
                reply_markup=keyboards.exit
                )
            self.update_state(message.chat.id, states.random_connect)

            # find another user to connect
            other_user = self.users.find_one(
                {
                'state': states.random_connect,
                'chat.id': {'$ne': message.chat.id}
                }
            )

            if not other_user:
                return

            # update status
            self.update_state(other_user["chat"]["id"], states.connected)
            self.update_state(message.chat.id, states.connected)

            # store connected users
            self.update_connection_id(other_user["chat"]["id"], message.chat.id)
            self.send_message(
                 other_user["chat"]["id"],
                f'Connected to {message.chat.id}',
                reply_markup=keyboards.exit
                )

            self.update_connection_id(message.chat.id, other_user["chat"]["id"])
            self.send_message(
                 message.chat.id,
                f'Connected to {other_user["chat"]["id"]}',
                reply_markup=keyboards.exit
                )

        @self.bot.message_handler(regexp = emoji.emojize(keys.exit))
        def exit(message):
            self.send_message(
                 message.chat.id,
                keys.exit,
                reply_markup=keyboards.main
                )
            self.update_state(message.chat.id, states.main)

            current_user = self.users.find_one(
                {'chat.id': message.chat.id}
            )
            if not current_user.get("connected_to"):
                return

            other_user = self.users.find_one(
                {'chat.id': current_user["connected_to"]}
            )
            # Terminate other user's connection.
            self.update_state(other_user["state"], states.main)
            self.send_message(
                other_user["chat"]["id"],
                f'Oops... the other user ended the chat\n {keys.exit}',
                reply_markup=keyboards.main
                )

            # reset connection id
            self.update_connection_id(current_user["chat"]["id"], None)
            self.update_connection_id(other_user["chat"]["id"], None)


        @self.bot.message_handler(func=lambda m: True)
        def echo(message):
            current_user = self.users.find_one(
                {'chat.id': message.chat.id}
            )

            if (current_user["state"] != states.connected) \
                or (current_user["connected_to"] is None):
                return

            self.send_message(
                current_user["connected_to"], message.text,
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

    def update_state(self, chat_id, user_state):
        """
        update user state.
        """
        self.users.update_one(
            {'chat.id': chat_id},
            {'$set': {'state': user_state}},
            upsert=True
            )

    def update_connection_id(self, chat_id, chat_id_other):
        """
        update user connected to id.
        """
        self.users.update_one(
            {'chat.id': chat_id},
            {'$set': {'connected_to': chat_id_other}},
            upsert=True
            )


if __name__ == '__main__':
    logger.info('Bot Started!')
    tlgrmbot = Bot(telebot=bot, db=mongodb)
    tlgrmbot.run()
