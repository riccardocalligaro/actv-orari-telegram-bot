import telebot, os, re
from requests.exceptions import ConnectionError
from flask import Flask, request
from telebot import types
from find_next_bus import find_next_times
from trova_orari import trova_tratta, trova_trips, trova_fermate, trova_fermata_corrispondenza
from elabora_posizione import elabora_coordinate
import requests
import time


token = os.environ['TELEGRAM_TOKEN']
bot = telebot.TeleBot(token)
server = Flask(__name__)



@bot.message_handler(commands=['start'])
def welcome_message(message):
    chat_id = message.chat.id
    name = message.from_user.first_name
    bot.send_message(chat_id, 'Ciao 👋🏻 '+ name, '''
    questo bot ti aiuta a trovare gli orari dei bus ACTV''')
    bot.send_message(chat_id, '''
    💡 Per ora le funzioni sono:
         \n🚏 /fermatabus Trova i prossimi bus che passano per una fermata (codice o posizone)
         \n🕒 /orari Trova gli orari di una tratta
         \nℹ️ /info Contattami per qualsiasi problema o consiglio per migliorare questo bot!

    ''',  parse_mode="Markdown")

@bot.message_handler(commands=['info'])
def select_tratta(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, '''
    *🖥️ Creato da: * [Riccardo Calligaro](tg://user?id=48837808)
    \n🌐 *Linguaggio:* Python 3.7 + Pandas
    \n📓 *Source code: *  [Github](https://github.com/riccardocalligaro/actvoraridev)
    \n📚 [Open Data](http://actv.avmspa.it/sites/default/files/attachments/opendata/)
    ''', parse_mode='Markdown')

# funzioni principali dei comandi
@bot.message_handler(commands=['fermatabus'])
def select_tratta(message):
    chat_id = message.chat.id
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button_geo = types.KeyboardButton(text="📍 Invia posizone", request_location=True)
    keyboard.add(button_geo)
    bot.send_message(chat_id,'''📍 Invia una posizione  attraverso il menu del pulsante 📎 accanto al campo testo o premi il pulsante sottostante.
🚏 Usa /codicefermata per inviare il codice della fermata.
    ''', reply_markup=keyboard)

@bot.message_handler(commands=['orari'])
def orari_linea(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "🚌 Inviare codice tratta (es.6E): ", reply_markup = types.ReplyKeyboardRemove(True))
    bot.register_next_step_handler(message, trova_codice)

@bot.message_handler(commands=['codicefermata'])
def codice_fermata(message):
    chat_id = message.chat.id
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button_immagine_fermata = types.KeyboardButton(text="❓ Dove trovo il codice fermata")
    keyboard.add(button_immagine_fermata)
    bot.send_message(chat_id, "🚏 Inviare codice fermata: ", reply_markup=keyboard)
    bot.register_next_step_handler(message, trova_orari_fermata)

@bot.message_handler(commands=['help'])
def messaggio_help(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, '''
    💡 Per ora le funzioni sono:
            \n🚌 /fermatabus Trova i prossimi bus che passano per una fermata (codice o posizone)
            \n🚏 /codicefermata Invia il codice di una fermata e trova i prossimi 5 bus che passeranno!
            \n🕒 /orari Trova gli orari di una tratta
            \nℹ️ /info Contattami per qualsiasi problema o consiglio per migliorare questo bot!

        ''',  parse_mode="Markdown", reply_markup = types.ReplyKeyboardRemove(True))
#funzioni /fermatabus

def trova_orari_fermata(message):
    chat_id = message.chat.id
    if message.text == '❓ Dove trovo il codice fermata':
        bot.send_photo(chat_id, open('codicefermatACTV.jpg', 'rb'), reply_markup = types.ReplyKeyboardRemove(True), caption="É un codice di massimo 4 cifre che si trova solitamente sul palo della fermata.")
        return
    bot.send_message(chat_id, "⚙️ Sto calcolando dammi qualche secondo...")

    try:
        bot.send_message(chat_id, find_next_times(message.text))
    except Exception as e:
        bot.send_message(chat_id, "🤨 La fermata inserita non esiste")
        print(e)


#funzioni /orari
def trova_codice(message):
    chat_id = message.chat.id
    try:
        bot.send_message(chat_id, trova_tratta(message.text))
        bot.send_message(chat_id, "🚍 Inserire ID: ")
        bot.register_next_step_handler(message, trova_trip)
    except Exception as e:
        bot.send_message(chat_id, "🤨 La fermata inserita non esiste, riprova /orari")
        print(e)


def trova_trip(message):
    trip = message.text
    chat_id = message.chat.id
    try:
        if not(trip.isnumeric()):
            bot.send_message(chat_id, "⛔️ Si é verificato un errore, riprovare.\n🤖 Traceback: input non é numerico")
            return
    except Exception as e:
         bot.send_message(chat_id, "⛔️ Si é verificato un errore, riprovare.\n🤖 Traceback: Nonetype non ha oggetto numerico")
    try:
        trova_trips(trip)
        bot.send_message(chat_id, "🚏 Inserisci la fermata (es. 'Castellana Cipressina'): ")
        bot.register_next_step_handler(message, inserisci_fermata)
    except Exception as e:
        bot.send_message(chat_id, "⛔️ Si é verificato un errore: numero non presente nella lista. Riprovare /orari")
        print(e)



def inserisci_fermata(message):
    chat_id = message.chat.id
    fermata = message.text

    try:
        output = trova_fermate(fermata)
        if output.isnumeric() == False:
            bot.register_next_step_handler(message, inserisci_id_fermata)
            bot.send_message(chat_id, output)
        else:
            bot.send_message(chat_id, output)
    except Exception as e:
        bot.send_message(chat_id, "⛔️ Si é verificato un errore, riprovare /orari")

def inserisci_id_fermata(message):
    chat_id = message.chat.id
    scelta = message.text
    try:
        bot.send_message(chat_id, "⚙️ Sto calcolando, per le fermate piú critiche ci puó volere qualche secondo.")
        bot.send_message(chat_id, trova_fermata_corrispondenza(scelta))
    except Exception as e:
        bot.send_message(chat_id, "🚧 Nessuna corrispondenza trovata, riprovare /orari")

@bot.message_handler(func=lambda message: message.text == '❓ Dove trovo il codice fermata')
def invia_immagine(message):
    chat_id = message.chat.id
    bot.send_photo(chat_id, open('codicefermatACTV.jpg', 'rb'), reply_markup = types.ReplyKeyboardRemove(True), caption="É un codice di massimo 4 cifre che si trova solitamente sul palo della fermata.")

@bot.message_handler(func=lambda message: message.text == '1248')
def invia_immagine(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "😅 Se hai provato a inserire il 1248 avendo visto la foto ti informo che la foto é vecchia e i codici sono stati modificati. Appena avró tempo provvederó a sostituirla con una piú secente. ")


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, '''
    😐 Non so rispondere a questa richiesta.
Puoi contattare @R1CCARD0 per avere informazioni sul mio funzionamento, o premere /help per una lista dei comandi supportati.''')

@bot.message_handler(func=lambda message: True, content_types=['location'])
def echo_all(message):
    chat_id = message.chat.id
    print("Posizione ricevuta")
    try:
        bot.send_message(chat_id, "⚙️ Sto calcolando dammi qualche secondo...")
        pos = elabora_coordinate(message.location.latitude, message.location.longitude)
        bot.send_message(chat_id,find_next_times(pos))
    except Exception as e:
        bot.send_message(chat_id,"😐 Non sono riuscito ad elaborare le coordinate. Errore: " + str(e))



bot.polling()


@server.route('/' + token, methods=['POST'])
def getMessage():
        bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
        return "!", 200


@server.route("/")
def webhook():
        bot.remove_webhook()
        bot.set_webhook(url='https://actv-telegram-bot.herokuapp.com/' + token)
        return "!", 200


if __name__ == "__main__":
     server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
