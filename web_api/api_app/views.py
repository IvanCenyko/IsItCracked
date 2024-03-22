from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

from bs4 import BeautifulSoup
import urllib.parse
from pathlib import Path
import requests
import os
import re

# format a string to URL query search format
def search_to_urlformat(string:str):
    return urllib.parse.quote_plus(string)


def normalize(string: str):
    # Remove unwanted characters
    string = re.sub(r"[':®™’]", "", string)
    
    # Remove version numbers like v1.0.2
    string = re.sub(r"v\d+(\.\d+)+", "", string)
    
    # Remove parentheses and their content
    string = re.sub(r"\(.*?\)", "", string)
    
    # Remove dashes and what follows
    string = re.sub(r"–.*", "", string)
    
    # Remove text after |
    string = re.sub(r"\|.*", "", string)
    
    # Lowercase the string
    return string.lower()

# Steam database search endpoint
class SteamDB(View):
    def __init__(self):
        self.SEARCH_URL = "https://store.steampowered.com/search/?category1=998&ndl=1&term="
    
    # GET method, takes a "search" argument
    def get(self, request):
        
        # if there's no search
        if not request.GET["search"]:
            return JsonResponse({"status": False})
        
        # convert to url query
        formatted_search = search_to_urlformat(request.GET["search"])
        #steam html data
        steam_raw_data = requests.get(self.SEARCH_URL + formatted_search).content



        # bs of result, filter only div with results
        results_soup = BeautifulSoup(steam_raw_data, "html.parser").find("div", id="search_resultsRows")

        try:
            # list of every result
            results_raw = results_soup.find_all("a")
        except AttributeError:
            return JsonResponse({"results": []})

        # for every result...
        results = []
        for result_raw in results_raw:
            # filter the name
            name = result_raw.find("span").text
            
            # append to result list
            results.append(name)

        # response
        return JsonResponse({"results" : results[:8]})



class CrackedSearchFitgirl(View):

    def __init__(self):
        self.FITGIRL_URL = "https://fitgirl-repacks.site/?s="

    # GET method, takes a "search" argument
    def get(self, request):

        ### GET RESULTS ###
        # if there's no search
        if not request.GET["search"]:
            return JsonResponse({"status": False})

        # take search and request to the web
        search = request.GET["search"]
        full_web = requests.get(self.FITGIRL_URL + search_to_urlformat(search)).content

        # bs with full web on html
        soup = BeautifulSoup(full_web, "html.parser")

        # list of results, every result is an article
        results_block = soup.find_all("article")

        # if there's no results
        if not results_block:
            # make a request to the web searching the text before ":",
            # (filter words like "definitive edition")
            search = normalize(request.GET["search"])
            full_web = requests.get(self.FITGIRL_URL + search.split(":", 1)[0]).content
            
            # bs of full web
            soup = BeautifulSoup(full_web, "html.parser")

            # filter results, every result is an article
            results_block = soup.find_all("article")

        # for every result
        data = {"results": []}
        for result in results_block:
            # scrap the h1
            result_title = result.find("h1")
            # scrap the title
            title = result_title.text
            # scrap game url
            url = result_title.find("a")["href"]

            # save it on data, with key being the game name
            data["results"].append({"game": title, "url": url})

        ### DELETE NOT COMPLETE MATCHING RESULTS ###
        
        # list of elements to delete
        to_delete = []
        # list of words of the user's search, normalized
        name_word_list = normalize(search).split(" ")
        # for every result from the source
        for result in data["results"]:
            # take the game name, and normalize it
            game_name = normalize(result["game"])

            # for every word in the user's search
            for word in name_word_list:
                # look if the word is on the result from source, if not...
                if not word in game_name:
                    # add that result to delete list
                    to_delete.append(result)
                    # breaks word checking and proceed to next result
                    break
                    
        # delete every element from data
        for i in to_delete:
            data["results"].remove(i)
        # response
        return JsonResponse(data)

    def post(self, request):
        ...
        
class CrackedSearchIGG(View):
    def __init__(self):
        self.IGGSEARCH = "https://igg-games.com/list-9163969989-game.html"

    def get(self, request):

        # if there's no search, return the method
        if not request.GET["search"]:
            return JsonResponse({"status": False})
        
        # normalized user's search
        search = normalize(request.GET["search"])

        # igg games games
        database_web = requests.get(self.IGGSEARCH).content

        # list of all cracked games on IGG
        all_games = BeautifulSoup(database_web, "html.parser").find_all("li")
        
        # pop last two elements, which are irrelevant buttons
        for _ in range(2):
            all_games.pop(-1)

        # for every game block
        games_list = {"results": []}
        for element in all_games:
            # take the name
            game = element.text
            # take the url
            a = element.find("a")
            url = a["href"]
            # append to dict
            games_list["results"].append({"game": game, "url": url})

        # for every cracked game on dict
        to_delete = []
        for element in games_list["results"]:
            # normalize its name
            game_normalized = normalize(element["game"])
            # for every word in the search
            for word in search.split(" "):
                # if it's not on the cracked game of this iteration
                if not word in game_normalized:
                    # append to delete list
                    to_delete.append(element)
                    break
        
        # delete every game that doesn't match all search elements
        for i in to_delete:
            games_list["results"].remove(i)
        
        # response
        return JsonResponse(games_list)

