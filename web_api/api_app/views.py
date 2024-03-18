from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver

from bs4 import BeautifulSoup
import urllib.parse
from pathlib import Path
import requests
import os

# funcion que formatea un string en el formato de busqueda de query URL
def search_to_urlformat(string):
    formatted_string = urllib.parse.quote_plus(string)
    return formatted_string

class Search(View):

    def __init__(self):

        self.SEARCH_URL = "https://omycrack.com/search?q=" 

    def get(self, request):
        # parametros de busqueda dados por el usuario
        search_params = search_to_urlformat(request.GET["search"])

        # Obtiene el directorio actual del archivo en el que se está ejecutando el script
        current_directory = Path(__file__).resolve().parent

        # Ruta al directorio donde se encuentra chromedriver
        chromedriver_path = str(current_directory / 'chromedriver_linux64' / 'chromedriver')

        # configura webdriver
        options = webdriver.FirefoxOptions()
        #options.add_argument('--disable-gpu')
        #options.add_argument('--no-sandbox')
        options.add_argument('--headless=new')
        #options.binary_location = "../chromedriver_linux64/chromedriver"
        #options.binary_location = chromedriver_path
        browser = webdriver.Firefox(options=options)
        
        # abre navegador y...
        with browser as browser:

            # request a la websource
            browser.get(self.SEARCH_URL + search_params)
            
            try:
                # espera a que aparezcan los resultados
                wait = WebDriverWait(browser, 20)
                wait.until(expected_conditions.presence_of_element_located((By.XPATH, "/html/body/div/div[2]/div/div[2]/div/div[2]/section[2]/div/div/div[2]")))
            except TimeoutException:
                return JsonResponse({"results": None})
            
            # arma un bloque html con los resultados
            results_block = browser.find_element(By.XPATH, "/html/body/div/div[2]/div/div[2]/div/div[2]/section[2]/div/div").get_attribute("innerHTML")
            
        # sopa de los resultados
        soup = BeautifulSoup(results_block, "html.parser")

        # hace una lista, cada uno es un resultado
        results = soup.find_all("div", class_="col-lg-3 col-md-6 col-sm-6 col-xs-12")

        # arma template de data
        data = {"results": {}}
        # para cada resultado en bloque html
        for result in results:
            
            # toma url y nombre del juego
            url = result.find("a")["href"]
            name = result.find("h4").text

            # hace una dict key con el nombre del juego y el url
            data["results"][name] = url

        return JsonResponse(data)

    def post(self, request):
        ...

class GameStatus(View):
    def __init__(self):
        ...
    def get(self, request):

        # toma el url del usuario
        url = request.GET["url"]

        # hace request al url del usuario
        html_block = requests.get(url).content

    
        soup = BeautifulSoup(html_block, "html.parser")

        # filtra el texto del status en la pagina
        status = soup.find("div", class_= "badge-item-g").text
        
        # borra caracteres indeseados
        status = status.replace("\n", "")

        if "Uncracked" in status:
            status = "Uncracked"
        
        if "Unreleased" in status:
            status = "Unreleased"

        # arma dict y devuelve json con el status
        data = {"status": status}

        return JsonResponse(data)

        
    def post(self, request):
        ...
