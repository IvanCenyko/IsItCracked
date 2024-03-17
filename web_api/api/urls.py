from django.urls import path
from . import views

urlpatterns = [
    path("search", views.Search.as_view(), name="search"),
    path("game-status", views.GameStatus.as_view(), name="game_status")
]
