from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

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
        self.FITGIRL_URL = "https://fitgirl-repacks.site/?s="

    def get(self, request):

        # si no hay busqueda
        if not request.GET["search"]:
            return JsonResponse({"status": False})

        # toma html de la web
        search = request.GET["search"]
        full_web = requests.get(self.FITGIRL_URL + search).content
        soup = BeautifulSoup(full_web, "html.parser")

        # filtro los resultados, c/u es un article
        results_block = soup.find_all("article")

        # para cada resultado...
        data = {}
        for result in results_block:
            # tomo el titulo h1
            result_title = result.find("h1")
            # saco el titulo del juego
            title = result_title.text
            # saco el url
            url = result_title.find("a")["href"]
            # lo guardo en el json a devolver
            data[title] = url
        
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
