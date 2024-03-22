from django.urls import path
from . import views

urlpatterns = [
    # endpoint that searches a game on steam
    path("steam-search", views.SteamDB.as_view(), name="steam_search"),
    # endpoint that searches a game on crack source
    path("cracked-search-fitgirl", views.CrackedSearchFitgirl.as_view(), name="cracked_search_fitgirl"),
    # endpoint that searches a game on crack source
    path("cracked-search-igg", views.CrackedSearchIGG.as_view(), name="cracked_search_igg")
    ]
