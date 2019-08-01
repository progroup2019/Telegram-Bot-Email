# coding=utf-8
import requests, wget
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputTextMessageContent
from telebot import types
from datetime import datetime
import re
from src.Imap import get_inbox, send_mail, verify_login

# token by @BotFather to the ProGroupBot
TOKEN = '754169521:AAFKQkWZzZBV6_ty2jJfmkXcwvPnBgCw3AM'

#User data
actual_chat_id = ""
email = ""
password = ""

#Email sender parameters
to = ""
subject = ""
content = ""
file_names = []

#Start bot
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

#Callback handler to yes or no response
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "cb_yes":
        #bot.send_message(call.message.chat.id, "Enter (connect:) your username and password separated by a space, to see your unread messages. For example: connect:user 12345 \n Enter (send_mail:) your username, password, to, subject and content, to send an email. For example: send_mail:user 12345 user2 hello good morning")
        msg = bot.send_message(call.message.chat.id, "Enter your email and password separated by a space.")
        bot.register_next_step_handler(msg, register_email_and_password)
    elif call.data == "cb_no":
        bot.send_message(call.message.chat.id, "Ok, I will be here yo help you")

# Register email and password to the actual user
def register_email_and_password(message):
    global email
    global password
    try:
        data = message.text.split(' ')
        email = data[0]
        password = data[1]
        result = verify_login(email, password)
        if (result ==  True):
            msg = bot.reply_to(message, "All ok you are connected to your mail, to disconect put 'disconect', do you want send an email or see your unread messages? (To see your unread messages put 'see unread messages' and to send put 'send mail')")
            bot.send_sticker(message.chat.id,"https://www.gstatic.com/webp/gallery/2.webp")
            bot.register_next_step_handler(msg, user_choice)
        else:
            msg = bot.reply_to(message, "Wrong user or password, please enter your email and password separated by a space.")
            bot.send_sticker(message.chat.id,"https://www.gstatic.com/webp/gallery/2.webp")
            bot.register_next_step_handler(msg, register_email_and_password)
       # bot.register_next_step_handler(msg, process_age_step)
    except Exception as e:
        print(e)
        bot.reply_to(message, 'oooops')

# Function to get the next steep to do for the user
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
        msg = bot.reply_to(message, "Unknown command, the commands available are: 'send mail, see unread mails and disconnect'")
        msg = bot.send_message(message.chat.id, "=D go another command!")
        bot.register_next_step_handler(msg, user_choice)

# Handle all sent documents of type 'text/plain'.
def get_file(message):
    global file_names
    if(message.content_type == 'document'):
        file_info = bot.get_file(message.document.file_id)
        file = wget.download('https://api.telegram.org/file/bot{0}/{1}'.format(TOKEN, file_info.file_path), out = "mail_attachment")
        file_names.append(file)
        print(file_names)
        bot.reply_to(message, "Document received, sir!, do you want to attach another file?")
    else:
        bot.reply_to(message, "Invalid format! do you want to attach another file?")
    bot.register_next_step_handler(message, send_mail_ask_for_files)

#Ask for files
def send_mail_ask_for_files(message):
    if(message.text.lower() == "yes"):
        msg = bot.reply_to(message, "Send the file that you want to attach")
        bot.register_next_step_handler(msg, get_file)
    elif(message.text.lower() == "no"):
        msg = bot.reply_to(message, "Place the content of the mail (example: Hi, this is my content.)")
        bot.register_next_step_handler(msg,send_mail_three)
    else:
        msg = bot.reply_to(message, "Wrong answer... Do you want to attach a file? (YES/NO)")
        bot.register_next_step_handler(msg, send_mail_ask_for_files)

#Set the To of the mail
def send_mail_one(message):
    global to
    pattern = re.compile('^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$')
    to = message.text.lower()
    if pattern.match(to):
        msg = bot.send_message(message.chat.id, "Place the subject of the mail (example: My Subject Oh Yeah)")
        bot.register_next_step_handler(msg, send_mail_two)
    else:
        msg = bot.reply_to(message, "Invalid format, please write again the receiver's email")
        bot.register_next_step_handler(msg, send_mail_one)

#Set the Subject of the mail
def send_mail_two(message):
    global subject
    subject = message.text
    msg = bot.send_message(message.chat.id, "Do you want to attach a file?")
    bot.register_next_step_handler(msg, send_mail_ask_for_files)

#Set the Content of the mail
def send_mail_three(message):
    global content
    global subject
    global to
    global file_names
    global email
    global password
    content = message.text
    if send_mail(content, to, subject, file_names, email, password):
        bot.send_message(message.chat.id, "Mail sent successfully")
    else:
        bot.send_message(message.chat.id, "Error sending mail")
    file_names = []
    msg = bot.send_message(message.chat.id, "=D Go another command! (See unread mails, send mail or disconnect")
    bot.register_next_step_handler(msg, user_choice)

# Handle all other messages
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    bot.reply_to(message, "Hello, if you are lost you can use the /help command and I will help you")

bot.polling()