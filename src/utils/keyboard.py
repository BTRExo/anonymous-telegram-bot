from telebot import types
import emoji

def create_keyboard(*keys, row_width=2,resize_keyboard=True):
    """
    create a keyboard from keys
    """
    keys = map(emoji.emojize, keys)
    buttons = map(types.KeyboardButton, keys)
    markup = types.ReplyKeyboardMarkup(
        row_width=row_width,
        resize_keyboard=resize_keyboard
        )
    markup.add(*buttons)
    return markup