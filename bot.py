import telebot
import schedule
import time
import json
import threading
from bs4 import BeautifulSoup
import urllib.parse
import requests

# Token del bot proporcionado por BotFather
TOKEN = '6553107234:AAFFmugu4WEvdrxFkKxMno7XIFR96qQBzNc'
SEARCH_API = 'https://steamcrackedgames.com/search/?q='
BASE_URL = 'https://steamcrackedgames.com'


# función para leer archivo JSON y convertirlo a un diccionario de Python
def leer_json(filename):
    # abre el archivo si existe
    try:
        with open(filename, 'r') as file:
            # convierte a dict
            data = json.load(file)
    # si el archivo no existe, devuelve un diccionario vacio
    except:
        data = {}
    return data

# función para escribir un diccionario de Python a un archivo JSON
def escribir_json(data, filename):
    # abro el archivo
    with open(filename, 'w') as file:
        # escribo el nuevo dict en el json
        json.dump(data, file, indent=4)

# funcion que formatea un string en el formato de busqueda de query URL
def formatear_busqueda(string):
    formatted_string = urllib.parse.quote_plus(string)
    return formatted_string

# agrega una URL al usuario
def agregar_url_a_usuario(user_id:str, url:str, filename:str):
    # Cargar db JSON
    data = leer_json(filename)

    # verificar si el usuario ya existe en el diccionario
    if user_id in data:
        # Verifica si la URL ya está en la lista del usuario
        if url in data[user_id]:
            # Sale de la función sin añadir la URL si ya está
            pass
        else:
            # Agrega la nueva URL a la lista existente
            data[user_id].append(url)
    else:
        # Crea una nueva dict key para el usuario con la nueva URL
        data[user_id] = [url]

    # Escribir los datos actualizados a la db JSON
    escribir_json(data, filename)

# funcion que busca los juegos en la API y devuelve bloques de HTML para cada resultado
def search(game):
    # URL de busqueda es el link base + la busqueda formateada
    api = SEARCH_API + formatear_busqueda(game)

    # hago request a la API
    search_web = requests.get(api).content

    # scrapeo resultados de la API
    soup = BeautifulSoup(search_web, "html.parser")
    
    # lista de resultados en bloques html
    list = soup.find_all("tr")

    games = []
    # para cada resultado, saco el bloque que contiene el nombre y el link
    for result in list:
        games.append(result.find("td"))

    return games

# Inicialización del bot
bot = telebot.TeleBot(TOKEN)

# Comando '/start' para explicar el bot
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.reply_to(message, "¡Hola! Soy un bot que avisa diariamente si los juegos que me digas están o no crackeados. "
                          "Puedes usar los siguientes comandos:\n"
                          "/add - Para añadir un juego marcado.\n"
                          "/remove - Para eliminar un juego marcado.\n"
                          "/status - Para ver el status actual de los juegos marcados.")

# Comando '/help' para describir los comandos
@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.reply_to(message, "Aquí tienes una lista de comandos disponibles:\n"
                          "/add <juego> - Añadir un juego marcado.\n"
                          "/remove - Eliminar un juego marcado.\n"
                          "/status - Para ver el status actual de los juegos marcados.")

# Comando '/add'
@bot.message_handler(commands=['add'])
def handle_add(message):
    # argumento
    arg = message.text.replace("/add", "")

    # si no hay argumento...
    if arg == '' or arg == None:
        bot.reply_to(message, "Falta argumento!")
    
    # si hay argumento...
    else:
        # Hace búsqueda en la API
        games = search(arg)

        # toma el nombre de cada resultado, para la UI
        results = []
        # para cada encuentro
        for game in games:
            # Intentar convertirlo en texto (puede no haber resultados, por eso el try)
            try:
                name = game.find("a").text
                # apendo a lista de nombres de los resultados
                results.append(name)
            except AttributeError:
                pass

        # si hay varios resultados, pide al usuario que elija uno
        if len(results) > 1:
            # crea un teclado personalizado con los resultados para que el usuario elija
            keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)

            # arma un iterable con un numero para cada resultado, y lo añado al teclado
            for i in enumerate(results, start=1):
                keyboard.add(str(i))

            # arma string con resultados
            ask_string = "Seleccione un resultado:\n"
            # para cada resultado, le pone el index numerico correspondiente del teclado
            for i in range(len(results)):
                ask_string += f"{i+1}: {results[i]}\n"
            
            # envia mensaje con la lista de resultados al usuario, pidiendo que elija uno
            bot.send_message(message.chat.id, ask_string, reply_markup=keyboard)

            # registra el handler para manejar la elección del usuario
            bot.register_next_step_handler(message, handle_add_choice, games, results)

        # Si hay un único resultado, mostrarlo directamente
        elif len(results) == 1:
            # toma el URL de la API
            url = BASE_URL + games[0].find("a")["href"]   
            # guarda a nombre del usuario
            agregar_url_a_usuario(str(message.chat.id), url, "data.json")

            bot.send_message(message.chat.id, f"{results[0]} añadido.")
        
        # si no hay resultados
        else:
            bot.send_message(message.chat.id, "No se encontraron resultados.")

# función para manejar la elección del usuario al añadir un juego
def handle_add_choice(message, games, results):

    # si el usuario responde con un numero...
    try:
        # toma su respuesta del teclado
        choice = int(message.text) - 1
        # scrapea el URL del juego en la API a partir de la respuesta del usuario
        url = BASE_URL + games[choice].find("a")["href"]
        # agrega el URL a los guardados por el usuario
        agregar_url_a_usuario(str(message.chat.id), url, "data.json")

        # cierra comando
        bot.send_message(message.chat.id, f"{results[choice]} añadido.", reply_markup=telebot.types.ReplyKeyboardRemove())
        # Limpiar el step handler
        bot.clear_step_handler(message)

    # si el usuario responde algo no valido, se cancela el comando
    except ValueError:
        bot.send_message(message.chat.id, "Comando cancelado.")
        bot.clear_step_handler(message)


# Comando '/remove'
@bot.message_handler(commands=['remove'])
def handle_remove(message):
    # ee la lista de URLs del usuario desde el archivo JSON
    user_id = str(message.chat.id)
    data = leer_json("data.json")

    # si el usuario tiene juegos almacenados...
    if user_id in data and data[user_id]:
        # crea un teclado personalizado con las URLs del usuario para que elija cuál eliminar
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        # para cada URL (juego) del usuario...
        for url in data[user_id]:
            # armo las opciones solo con el nombre del juego, quitando el resto del url almacenado
            keyboard.add(url.replace(f"{BASE_URL}/games/", ""))

        # envia mensaje al usuario pidiendo que elija un juego para eliminar de su lista
        bot.send_message(message.chat.id, "Seleccione un juego para eliminar:", reply_markup=keyboard)

        # Registra el handler para manejar la elección del usuario
        bot.register_next_step_handler(message, handle_remove_choice)

    else:
        bot.reply_to(message, "No tienes juegos almacenados.")

# función para manejar la elección del usuario al eliminar un juego
def handle_remove_choice(message):
    # Leer la lista de URLs del usuario desde el archivo JSON
    user_id = str(message.chat.id)
    data = leer_json("data.json")
    # Obtiene la URL del juego seleccionado
    url_to_remove = BASE_URL + "/games/" + message.text
    
    # si el URL esta en el usuario
    if url_to_remove in data[user_id]:
        # remueve la URL de los juegos guardados por el usuario
        data[user_id].remove(url_to_remove)
        escribir_json(data, "data.json")

        # envía un mensaje de confirmación al usuario
        bot.send_message(message.chat.id, f"Eliminado correctamente.")
        # elimina el teclado personalizado
        bot.send_message(message.chat.id, "Comando 'remove' cerrado.", reply_markup=telebot.types.ReplyKeyboardRemove())

    # si el usuario responde algo erroneo...
    else:
        # elimina el teclado personalizado
        bot.send_message(message.chat.id, "Comando 'remove' cerrado. No se hicieron cambios", reply_markup=telebot.types.ReplyKeyboardRemove())

    # limpia el next step handler
    bot.clear_step_handler(message)

@bot.message_handler(commands=['status'])
def handle_status(message):
    # lee el json
    data = leer_json("data.json")
    # si el usuario no tiene juegos guardados...
    if not str(message.chat.id) in data or data[str(message.chat.id)] == []:
        bot.reply_to(message, "No hay juegos guardados.")
    
    else:
        # armo string de lista de juegos
        status_string = 'Juegos marcados:\n'
        # para cada juego marcado por el usuario, usa su URL
        for url in data[str(message.chat.id)]:
            # hago request
            web = requests.get(url).content
            # busco la informacion
            soup = BeautifulSoup(web, 'html.parser')
            block = soup.find("div", class_="col-md-6 gameinfo mb-3")
            info = block.find_all("dd")
            name = info[0].text.replace("\n", "")
            status = info[2].text.replace("\n", "")

            # armo linea del juego y su status
            status_string += f"-{name}: {status}\n"

        bot.reply_to(message, status_string)

# handler para comandos desconocidos, se activa si un comando que comienza con '/' no existe
@bot.message_handler(func=lambda message: True if message.text and message.text.startswith('/') else False)
def handle_unknown_command(message):
    bot.reply_to(message, "Lo siento, no entendí ese comando. Puedes usar /help para ver la lista de comandos disponibles.")

# función que se ejecutará una vez por dia
def tarea_programada():
    # leo db
    data = leer_json("data.json")

    # para cada usuario
    for user in data:
        # armo string de lista de juegos
        status_string = 'Juegos marcados:\n'
        # para cada juego marcado por el usuario, uso su URL
        for url in data[user]:
            # hago request
            web = requests.get(url).content
            # busco la informacion
            soup = BeautifulSoup(web, 'html.parser')
            block = soup.find("div", class_="col-md-6 gameinfo mb-3")
            info = block.find_all("dd")
            name = info[0].text.replace("\n", "")
            status = info[2].text.replace("\n", "")

            # armo linea del juego y su status
            status_string += f"-{name}: {status}\n"
        bot.send_message(int(user), status_string)

# thread del bot
def polling_thread():
    while True:
        bot.polling()


# programación para ejecutarse diariamene
schedule.every().day.at("16:00").do(tarea_programada)

# thread de funcion que se ejecuta una vez por dia
def schedule_thread():
    while True:
        schedule.run_pending()
        time.sleep(60)  # Esperar 60 segundos antes de volver a comprobar


# inician los threads
polling_thread = threading.Thread(target=polling_thread)
schedule_thread = threading.Thread(target=schedule_thread)

polling_thread.start()
schedule_thread.start()




