from telethon import TelegramClient, events
from requests.auth import HTTPBasicAuth
from datetime import timedelta, datetime

import requests
import json
import sys
import os
import logging
import re
import traceback
import json
import signal
import time as t

try:
	with open("config.json") as f:
		config = json.load(f)
except:
	error_info = traceback.format_exc()
	print("Falha para carregar a configuração em Config.Json. Error: " + str(error_info))
	sys.exit(1)

bot_file_place = f"{os.getcwd()}/bot_telegram"

bot = TelegramClient(
	bot_file_place,
	int(config["telegram_bot"]["api_id"]),
	config["telegram_bot"]["api_hash"],
).start(bot_token=config["telegram_bot"]["api_token"])

bot.parse_mode = "html"

logging.basicConfig(
	format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s", level=logging.ERROR
)

CONVERSATION_STATE = {}
STATUS_EMAIL = 1
STATUS_IN_CONFIRMED = 2


def get_last_code_transaction(email):
	""" You need to store your WebhooksYou need provide a service that allow the Bot reads the last code transaction """
	url_request = f"{verify_url['telegram_bot']}/{email}"
	try:
		response = requests.get(url=url_request, verify=True)
	except Exception as e:
		logging.error(e)
		return False

	try:
		to_json = response.json()
	except:
		error_info = traceback.format_exc()
		logging.error(error_info)

	return to_json["code"]


def cancel_signature(email):
	last_code = get_last_code_transaction(email)

	try:
		url_request = "https://prd-api.mycheckout.com.br/api/v1/payment/refund/reason"
		response = requests.post(
			url=url_request,
			data={
				"codeTransaction": get_last_code_transaction(email),
				"email": email,
				"reason": "Não conseguirei assumir o compromisso financeiro",
				"comment": "não",
				"bankAccount": None,
			},
			verify=True,
		)
	except Exception as e:
		logging.error(e)
		return False

	code_status = response.status_code
	if code_status != 200:
		logging.error(
			f"Cancelamento para a assinatura {email} retornou um erro {code_status}"
		)
		return False

	to_json = None
	try:
		to_json = response.json()
	except:
		error_info = traceback.format_exc()
		logging.error(error_info)

	return to_json


@bot.on(events.NewMessage(pattern="/cancelar"))
async def cancel_request_bot_handler(event):
	user_id = event.sender_id

	message = event.message
	text = message.message.strip()

	try:
		state = CONVERSATION_STATE[user_id]
	except:
		await event.respond("Você não tem nada para cancelar.")
		raise events.StopPropagation

	state["email"] = None
	state["status"] = None

	await event.respond("Ação cancelada. Você pode estar usando o comando novamente.")
	raise events.StopPropagation


@bot.on(events.NewMessage(pattern="/assinatura"))
async def cancel_signature_bot_handler(event):
	global CONVERSATION_STATE

	user_id = event.sender_id

	message = event.message
	text = message.message.strip()

	# Verifica se o usuário pode estar usando essa ação
	try:
		state = CONVERSATION_STATE[user_id]
	except:
		CONVERSATION_STATE[user_id] = {
			"email": None,
			"status": None,
		}
		state = CONVERSATION_STATE[user_id]

	if state["status"] == None:
		await event.respond(
			"Por favor me informe o e-mail do cliente para estarmos pedindo cancelamento da assinatura."
		)

		CONVERSATION_STATE[user_id]["status"] = STATUS_EMAIL

	raise events.StopPropagation


@bot.on(events.NewMessage)
async def handler(event):
	message = event.message
	text = message.message.lower().strip()
	user_id = event.sender_id

	try:
		state = CONVERSATION_STATE[user_id]
	except:
		return False

	if state["status"] == STATUS_EMAIL:
		CONVERSATION_STATE[user_id]["email"] = text
		CONVERSATION_STATE[user_id]["status"] = STATUS_IN_CONFIRMED

		await event.respond(
			"Você tem certeza que deseja cancelar a assinatura do usuário %s. Digite <strong>SIM</strong> ou <strong>NÃO</strong>."
			% (state["email"])
		)

	elif state["status"] == STATUS_IN_CONFIRMED:
		action_to_do = None
		if text == "sim" or text == "yes" or text == "si":
			action_to_do = 1
		elif text == "no" or text == "nao" or text == "não":
			action_to_do = 2

		if action_to_do == None:
			await event.respond("Por favor dê uma resposta válida")
			raise events.StopPropagation
		elif action_to_do == 2:
			CONVERSATION_STATE[user_id]["email"] = None
			CONVERSATION_STATE[user_id]["status"] = None

			await event.respond("Ok, cancelado.")
			raise events.StopPropagation

		await event.respond("Por favor aguarde ...")
		result = cancel_signature(state["email"])
		if not result:
			await event.respond("Falha para obter resposta da API.")
		else:
			await event.respond(result)

		CONVERSATION_STATE[user_id]["email"] = None
		CONVERSATION_STATE[user_id]["status"] = None


def signal_handler(signal_number, frame):
	print("Received signal " + str(signal_number) + ". Trying to end tasks and exit ...")
	sys.exit(0)


if __name__ == "__main__":
	print("Bot sendo iniciado ...")

	signal.signal(signal.SIGINT, signal_handler)

	print("Bot iniciado.")
	bot.run_until_disconnected()
