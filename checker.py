from flask import Flask, request
#import psycopg2 as pg
import requests
import hashlib
import telebot
import os

telegram_api=os.environ["telegram"]
bot = telebot.TeleBot(telegram_api)

url = "https://speller.yandex.net/services/spellservice.json"

@bot.message_handler(commands=["help"])
def help(message):
	print("test")
	bot.send_message(message.chat.id, "Hello")

@bot.message_handler(commands=["test"])
def test(message):
	print("test")
	param={"lang":"ru,en,uk", "text": message.text, "options":6}
	print(param)
	corr = requests.post(url+"/checkText", data=param).json()
	print(corr, len(cor))
	if not corr: return
	text=message.text
	print(text)
	for i in corr:
		text.replace(corr[0]["word"],corr[0]["s"][0])
	bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda message: True)
def checker(message):
	param={"lang":"ru,en,uk", "text": message.text, "options":6}
	corr = requests.post(url+"/checkText", data=param).json()
	if not corr:
		return
	text=message.text
	print(text)
	for i in corr:
		text.replace(corr[0]["word"],corr[0]["s"][0])
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