# coding=utf-8

import telebot # Importamos las librería
#pip install pyTelegramBotAPI
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputTextMessageContent
from telebot import types
from datetime import datetime
import re
from src.Imap import *

from src.Imap import get_inbox

TOKEN = '754169521:AAFKQkWZzZBV6_ty2jJfmkXcwvPnBgCw3AM' # token by @BotFather

#User data
actual_chat_id = ""
email = ""
password = ""

#email sender parameters
to = ""
subject = ""
content = ""
file_names = []

bot = telebot.TeleBot(TOKEN)

#form to yes and no questions
def gen_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("Yes", callback_data="cb_yes"), InlineKeyboardButton("No", callback_data="cb_no"))
    return markup

# Handle '/help'
@bot.message_handler(commands=['help'])
def explain_bot_process(message):
    explain = "Hello, this is a bot that will help you see your inbox and send emails with just a few commands, to start this process you must type the command '/start'"
    bot.send_message(message.chat.id, explain)

# Handle '/start'
@bot.message_handler(commands=['start'])
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
        #bot.send_message(call.message.chat.id, "Enter (connect:) your username and password separated by a space, to see your unread messages. For example: connect:user 12345 \n Enter (send_mail:) your username, password, to, subject and content, to send an email. For example: send_mail:user 12345 user2 hello good morning")
        msg = bot.send_message(call.message.chat.id, "Enter your email and password separated by a space.")
        bot.register_next_step_handler(msg, registerEmailAndPassword)
    elif call.data == "cb_no":
        bot.send_message(call.message.chat.id, "Ok, I will be here yo help you")


def registerEmailAndPassword(message):
    global email
    global password
    try:
        data = message.text.split(' ')
        email = data[0]
        password = data[1]
        result = verifyLogin(email, password)
        if (result ==  True):
            msg = bot.reply_to(message, "All ok you are connected to your mail, to disconect put 'disconect', do you want send an email or see your unread messages? (To see your unread messages put 'see unread messages' and to send put 'send mail')")
            bot.send_sticker(message.chat.id,"https://www.gstatic.com/webp/gallery/2.webp")
            bot.register_next_step_handler(msg, user_choice)
        else:
            msg = bot.reply_to(message, "Wrong user or password, please enter your email and password separated by a space.")
            bot.send_sticker(message.chat.id,"https://www.gstatic.com/webp/gallery/2.webp")
            bot.register_next_step_handler(msg, registerEmailAndPassword)
       # bot.register_next_step_handler(msg, process_age_step)
    except Exception as e:
        print(e)
        bot.reply_to(message, 'oooops')

def user_choice(message):
    global email
    global password
    if message.text.lower() == "see unread messages":
        mails = get_inbox(email, password)
        for mail in mails:
            bot.send_message(message.chat.id, mail)
        msg = bot.send_message(message.chat.id, "=D go another command!")
        bot.register_next_step_handler(msg, user_choice)
    elif message.text.lower() == "send mail":
        msg = bot.send_message(message.chat.id, "Who do you want to send the mail to? (put the email correct, example: example@yopmail.com)")
        bot.register_next_step_handler(msg, send_mail_one)
    elif message.text.lower() == "disconnect":
        email = ""
        password = ""
        bot.reply_to(message,"You have disconnected, to reconnect remember to use the '/start' command to start my process again")
    else:
        msg = bot.reply_to(message, "Unknown command, the commands available are: 'send mail, see unread mails and disconect'")
        msg = bot.send_message(message.chat.id, "=D go another command!")
        bot.register_next_step_handler(msg, user_choice)

#Set the To of the mail
def send_mail_one(message):
    global to
    to = message.text.lower()
    msg = bot.send_message(message.chat.id, "Place the subject of the mail (example: My Subject Oh Yeah)")
    bot.register_next_step_handler(msg, send_mail_two)

#Set the Subject of the mail
def send_mail_two(message):
    global subject
    subject = message.text
    msg = bot.send_message(message.chat.id, "Place the content of the mail (example: Hi, this is my content.)")
    bot.register_next_step_handler(msg, send_mail_three)

#Set the Content of the mail
def send_mail_three(message):
    global content
    global subject
    global to
    global file_names
    global email
    global password
    content = message.text
    if sendMail(content, to, subject, file_names, email, password):
        bot.send_message(message.chat.id, "Mail sent successfully")
    else:
        bot.send_message(message.chat.id, "Error sending mail")
    msg = bot.send_message(message.chat.id, "=D Go another command!")
    bot.register_next_step_handler(msg, user_choice)



# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def message_type(message):
    pattern = re.compile('^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$')
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
    elif message.text[0:10].lower()=='send_mail:':
        data = message.text.split(' ')
        user = data[0][10:]
        password = data[1]
        to = data[2]
        subject = data[3]
        content = " ".join(data[4:])
        file_names = []
        if pattern.match(to):
            if sendMail(content, to, subject, file_names, user, password):
                bot.reply_to(message, "Email sended correctly")
            else:
                bot.reply_to(message, "Error sending mail")
        else:
            bot.reply_to(message,"Receiver's email invalid")
    else:
        bot.reply_to(message, "Wrong command, write /help to obtain information about the commands enableds")

    # bot.sendSticker(message.)
# Enable saving next step handlers to file "./.handlers-saves/step.save".
# Delay=2 means that after any change in next step handlers (e.g. calling register_next_step_handler())
# saving will hapen after delay 2 seconds.
bot.enable_save_next_step_handlers(delay=2)

# Load next_step_handlers from save file (default "./.handlers-saves/step.save")
# WARNING It will work only if enable_save_next_step_handlers was called!
bot.load_next_step_handlers()

bot.polling()