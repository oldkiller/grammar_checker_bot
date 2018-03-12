from flask import Flask, request
import psycopg2 as pg
import requests
import hashlib
import telebot
import os

data = pg.connect(os.environ["DATABASE_URL"])
data.set_isolation_level(pg.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
curs=data.cursor()

bot = telebot.TeleBot(os.environ["telegram"])

url = "https://speller.yandex.net/services/spellservice.json"

def isMyMessage(text):
	text=text.split()[0]
	text=text.split("@")
	if len(text)>1:
		if text[1]=="GrammarChecker_bot":
			return True
		else: return False
	return True

@bot.message_handler(commands=["start"])
def start(message):
	if not isMyMessage(message.text): return
	curs.execute("insert into chatsetting values(%s,%s) " +
		"on conflict(chat) do update set working=%s",
		(message.chat.id,True,True))
	text="Привет, теперь я буду следить за "+
		"орфографическими ошибками в этом чате."
	bot.send_message(message.chat.id, text)

@bot.message_handler(commands=["help"])
def help(message):
	if not isMyMessage(message.text): return
	text="Привет. Я бот, который исправляет сообщения с ошибками.\
	\n/check_off - для отключения проверки\
	\n/check_on - для включения проверки\
	\n/help - для помощи"
	bot.send_message(message.chat.id,text)

@bot.message_handler(commands=["check_off"])
def check_off(message):
	if not isMyMessage(message.text): return
	curs.execute("insert into chatsetting values(%s,%s) " +
		"on conflict(chat) do update set working=%s",
		(message.chat.id,False,False))
	text="Хорошо-хорошо, не смотрю. Пишите, как хотите."
	bot.send_message(message.chat.id, text)

@bot.message_handler(commands=["check_on"])
def check_off(message):
	if not isMyMessage(message.text): return
	curs.execute("insert into chatsetting values(%s,%s) " +
		"on conflict(chat) do update set working=%s",
		(message.chat.id,True,True))
	text="Так, что тут у нас. Теперь я буду следить за вашей орфографией"
	bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda message: True)
def checker(message):
	if not isMyMessage(message.text): return
	param={"lang":"ru,en,uk", "text": message.text}
	corr = requests.post(url+"/checkText", data=param).json()
	if not corr: return
	text=message.text
	for cor in corr:
		text=text.replace(cor["word"],cor["s"][0])
	bot.send_message(message.chat.id, text)

#Дальнейший код используется для установки удаления вебхуков
server = Flask(__name__)

@server.route("/bot", methods=['POST'])
def getMessage():
	bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
	return "!", 200

@server.route("/")
def webhook_add():
	bot.remove_webhook()
	bot.set_webhook(url="https://grammarcheckerbot.herokuapp.com/bot")
	return "!", 200

@server.route("/<password>")
def webhook_del(password):
	pasw=hashlib.md5(bytes(password, encoding="utf-8")).hexdigest()
	if pasw=="5b4ae01462b2930e129e31636e2fdb68":
		bot.remove_webhook()
		return "Webhook removed", 200
	else:
		return "Invalid password", 200

server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))