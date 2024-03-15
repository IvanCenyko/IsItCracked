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


# Función para leer un archivo JSON y convertirlo a un diccionario de Python
def leer_json(filename):
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
    except:
        data = {}
    return data

# Función para escribir un diccionario de Python a un archivo JSON
def escribir_json(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

def formatear_busqueda(string):
    # Convertir otros caracteres especiales según la codificación de URL
    formatted_string = urllib.parse.quote_plus(string)
    return formatted_string

def agregar_url_a_usuario(user_id:str, url:str, filename:str):
    # Cargar datos existentes del archivo JSON
    data = leer_json(filename)

    # Verificar si el usuario ya existe en el diccionario
    if user_id in data:
        # Verificar si la URL ya está en la lista del usuario
        if url in data[user_id]:
            # Salir de la función sin añadir la URL si ya está presente
            pass
        else:
            # Agregar la nueva URL a la lista existente
            data[user_id].append(url)
    else:
        # Crear una nueva entrada para el usuario con la nueva URL
        data[user_id] = [url]

    # Escribir los datos actualizados de vuelta al archivo JSON
    escribir_json(data, filename)


def search(game):
    api = SEARCH_API + formatear_busqueda(game)

    search_web = requests.get(api).content

    soup = BeautifulSoup(search_web, "html.parser")
    
    list = soup.find_all("tr")

    games = []
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
    # Argumento
    arg = message.text.replace("/add", "")

    # Si no hay argumento...
    if arg == '' or arg == None:
        bot.reply_to(message, "Falta argumento!")
    
    # Si hay argumento...
    else:
        # Hacer búsqueda en la API
        games = search(arg)

        # Tomar el nombre de cada resultado para la UI
        results = []
        # Para cada encuentro
        for game in games:
            # Intentar convertirlo en texto (puede no haber resultados, por eso el try)
            try:
                name = game.find("a").text
                results.append(name)
            except AttributeError:
                pass

        # Si hay varios resultados, pedir al usuario que elija uno
        if len(results) > 1:
            # Crear un teclado personalizado con los resultados para que el usuario elija
            keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            for i, result in enumerate(results, start=1):
                keyboard.add(str(i))

            # Armar string con resultados
            ask_string = "Seleccione un resultado:\n"
            for i in range(len(results)):
                ask_string += f"{i+1}: {results[i]}\n"
            
            # Enviar mensaje al usuario pidiendo que elija un resultado
            bot.send_message(message.chat.id, ask_string, reply_markup=keyboard)

            # Registrar el manejador para manejar la elección del usuario
            bot.register_next_step_handler(message, handle_add_choice, games, results)

        # Si hay un único resultado, mostrarlo directamente
        elif len(results) == 1:
            # Tomar el URL de la API
            url = BASE_URL + games[0].find("a")["href"]   
            # Guardarlo a nombre del usuario
            agregar_url_a_usuario(str(message.chat.id), url, "data.json")

            bot.send_message(message.chat.id, f"{results[0]} añadido.")
        
        # Si no hay resultados
        else:
            bot.send_message(message.chat.id, "No se encontraron resultados.")

# Función para manejar la elección del usuario al añadir un juego
def handle_add_choice(message, games, results):

    try:
        # Tomar su respuesta del teclado
        choice = int(message.text) - 1
        # Sacar el URL del juego en la API a partir de la respuesta del usuario
        url = BASE_URL + games[choice].find("a")["href"]
        # Agregar el URL a los guardados por el usuario
        agregar_url_a_usuario(str(message.chat.id), url, "data.json")

        # Cerrar
        bot.send_message(message.chat.id, f"{results[choice]} añadido.", reply_markup=telebot.types.ReplyKeyboardRemove())
        # Limpiar el manejador de pasos siguientes
        bot.clear_step_handler(message)

    except ValueError:
        bot.send_message(message.chat.id, "Comando cancelado.")
        bot.clear_step_handler(message)


# Comando '/remove'
@bot.message_handler(commands=['remove'])
def handle_remove(message):
    # Leer la lista de URLs del usuario desde el archivo JSON
    user_id = str(message.chat.id)
    data = leer_json("data.json")

    # Verificar si el usuario tiene URLs almacenadas
    if user_id in data and data[user_id]:
        # Crear un teclado personalizado con las URLs del usuario para que elija cuál eliminar
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        for url in data[user_id]:
            # armo las opciones solo con el nombre del juego, quitando el resto del url
            keyboard.add(url.replace(f"{BASE_URL}/games/", ""))

        # Enviar mensaje al usuario pidiendo que elija una URL para eliminar
        bot.send_message(message.chat.id, "Seleccione un juego para eliminar:", reply_markup=keyboard)

        # Registrar el manejador para manejar la elección del usuario
        bot.register_next_step_handler(message, handle_remove_choice)

    else:
        bot.reply_to(message, "No tienes juegos almacenados.")

# Función para manejar la elección del usuario al eliminar un juego
def handle_remove_choice(message):
    # Leer la lista de URLs del usuario desde el archivo JSON
    user_id = str(message.chat.id)
    data = leer_json("data.json")
    # Obtiene la URL del juego seleccionado
    url_to_remove = BASE_URL + "/games/" + message.text
    
    # si el URL esta en el usuario
    if url_to_remove in data[user_id]:
        # Remueve la URL de los juegos guardados por el usuario
        data[user_id].remove(url_to_remove)
        escribir_json(data, "data.json")

        # Envía un mensaje de confirmación al usuario
        bot.send_message(message.chat.id, f"Eliminado correctamente.")
        # Elimina el teclado personalizado
        bot.send_message(message.chat.id, "Comando 'remove' cerrado.", reply_markup=telebot.types.ReplyKeyboardRemove())
    else:
        # Elimina el teclado personalizado
        bot.send_message(message.chat.id, "Comando 'remove' cerrado. No se hicieron cambios", reply_markup=telebot.types.ReplyKeyboardRemove())

    # Limpiar el manejador de pasos siguientes
    bot.clear_step_handler(message)

@bot.message_handler(commands=['status'])
def handle_status(message):
    # leo el json
    data = leer_json("data.json")
    # si el usuario no tiene juegos guardados...
    if not str(message.chat.id) in data or data[str(message.chat.id)] == []:
        bot.reply_to(message, "No hay juegos guardados.")
    
    else:
        # armo string de lista de juegos
        status_string = 'Juegos marcados:\n'
        # para cada juego marcado por el usuario, uso su URL
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

# Manejador para comandos desconocidos
@bot.message_handler(func=lambda message: True if message.text and message.text.startswith('/') else False)
def handle_unknown_command(message):
    bot.reply_to(message, "Lo siento, no entendí ese comando. Puedes usar /help para ver la lista de comandos disponibles.")


# Función que se ejecutará programáticamente según un horario
def tarea_programada():
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

# Función para ejecutar el bot.polling()
def polling_thread():
    while True:
        bot.polling()


# Programación de una tarea para ejecutarse diariamente a las 23:29
schedule.every().day.at("16:00").do(tarea_programada)

# Función para ejecutar el schedule.run_pending()
def schedule_thread():
    while True:
        schedule.run_pending()
        time.sleep(60)  # Esperar 60 segundos antes de volver a comprobar


# Iniciar los threads
polling_thread = threading.Thread(target=polling_thread)
schedule_thread = threading.Thread(target=schedule_thread)

polling_thread.start()
schedule_thread.start()




