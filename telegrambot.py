import telebot # Importamos las librería
#pip install pyTelegramBotAPI
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputTextMessageContent
from telebot import types
from datetime import datetime

from src.Imap import get_inbox

TOKEN = '839372173:AAE11WbqFHXUQyxCgk9erTpiJWi9rGg8ctw' # token by @BotFather
actual_chat_id = ""
def connect_email(user, password):
    mails = get_inbox(user, password)
    return True, mails

bot = telebot.TeleBot(TOKEN)

#form to yes and no questions
def gen_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("Yes", callback_data="cb_yes"), InlineKeyboardButton("No", callback_data="cb_no"))
    return markup

# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    hour = datetime.now().hour
    if 18 > hour >=12:
        time = "Good afternoon!"
    elif (6<= hour < 12):
        time = "Good morning!"
    else:
        time = "Good evening!"

    options_message = time + "\nDo you want to connect to your email service?"
    actual_chat_id = message.chat.id
    bot.send_message(actual_chat_id, options_message, reply_markup=gen_markup())

#callback handler to yes or no response
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "cb_yes":
        bot.send_message(call.message.chat.id, "Enter (connect:) your username and password separated by a space, for example: connect:user 12345")
    elif call.data == "cb_no":
        bot.send_message(call.message.chat.id, "Ok, I will be here yo help you")



# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def message_type(message):
    if message.text[0:8].lower()=='connect:':
        data = message.text.split(' ')
        user = data[0][8:]
        password = data[1]
        connected, mails = connect_email(user,password)
        if connected:
            bot.reply_to(message, "Nice")
            bot.send_sticker(message.chat.id,"https://www.gstatic.com/webp/gallery/2.webp")
            bot.send_message(message.chat.id, "This is your mailbox :D")
            for mail in mails:
                bot.send_message(message.chat.id, mail)
        else:
            bot.reply_to(message, "Mail or password wrong")
            bot.send_sticker(message.chat.id,"https://www.gstatic.com/webp/gallery/5.webp")
    # bot.sendSticker(message.)

bot.polling()