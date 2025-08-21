from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("categories", views.categories, name="categories"),
    path("auction/<str:title>/", views.auctions, name="auctions"),
    path("newListing", views.creatNewListing, name="creatNewListing"),
    path("watchlist/", views.watchlist_page, name="watchlist_page"),
    path("watchlist/<int:auctionID>/", views.add_to_watchlist, name="add_to_watchlist"),
    path("watchlist/remove/<int:auctionID>/", views.remove_from_watchlist, name="remove_from_watchlist"),
    path("auction/<int:auction_id>/bid/", views.place_bid, name="place_bid"),
    path("auction/remove/<int:auctionID>/",views.remove_from_activeListing , name="remove_from_activeListing"),
    path("auction/<int:auction_id>/comment/", views.add_comment, name="add_comment"),
]
