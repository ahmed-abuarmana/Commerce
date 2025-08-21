from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import User, Auctions, Watchlist, Bids, Comments

auctions_list = Auctions.objects.all()

def get_winner_of_auction(auc):
    highest_bid = Bids.objects.filter(auction=auc).order_by('-amount').first()
    winner_user = None
    if highest_bid:
        winner_user = highest_bid.user
    return winner_user

# All auctions list
def index(request):
    return render(request, "auctions/index.html", {
        "auctions": auctions_list
    })


def login_view(request):
    if request.method == "POST":
        
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            next_url = request.POST.get("next")
            if next_url: 
                return redirect(next_url)
            else:
                return HttpResponseRedirect(reverse("index"))
        
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
        
    else:
        return render(request, "auctions/login.html", {
            "next": request.GET.get("next", "")
        })


@login_required(login_url="/login")
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def categories(request):
    categories_list = Auctions.objects.values_list('category', flat=True).distinct()
    category_name = request.GET.get('category')
    categorie_filter = Auctions.objects.filter(category=category_name)

    return render(request, "auctions/categories.html", {
        "categories": categories_list,
        "categorie_filter": categorie_filter
    })


def auctions(request, title):
    auc = Auctions.objects.filter(title=title).order_by('-title').first()
    if auc.active:
        # Determine who is last bid user
        cond1 = False
        last_bid_user = None 
        last_bid = Bids.objects.filter(auction__title=title).order_by('-id').first()
        if last_bid:
            last_bid_user = last_bid.user
            if request.user == last_bid.user:
                cond1 = True
        
        # Determine who is have this auction
        cond2 = False
        user_have_auction = Auctions.createdBy
        current_user = request.user
        if user_have_auction == current_user:
            cond2 = True
        
        # Import comments details
        comments = Comments.objects.filter(auction=auc).order_by("-id")

        return render(request, "auctions/auction.html", {
            "auction_details": Auctions.objects.filter(title=title),
            "last_bid_user": last_bid_user,
            "current_user": current_user,
            "cond1": cond1,
            "cond2": cond2, 
            "comments": comments
        })
    else:
        return redirect("remove_from_activeListing", auctionID=auc.id)


@login_required(login_url="/login")
def creatNewListing(request):
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        startingBid = request.POST.get("bid")
        imageURL = request.POST.get("imageURL")
        category = request.POST.get("category")

        if not title or not description or not startingBid:
            return render(request, 'auctions/NewListing.html', {
            "categories": Auctions.objects.values_list('category', flat=True).distinct(),
            "errorMessage": "Try again and fill Title, Desccription & Starting Bid field at least.",
            })
        
        new_listing = Auctions(
        title=title,
        description=description,
        startingBid=startingBid,
        imageURL=imageURL,
        category=category,
        createdBy = request.user
    )
        new_listing.save()
        return redirect("auctions", title=title)
    else:
        return render(request, "auctions/newListing.html", {
            "categories": Auctions.objects.values_list('category', flat=True).distinct(),
            "errorMessage": "Full all fields please"
        })

@login_required
def remove_from_activeListing(request, auctionID):
    auc = Auctions.objects.filter(id= auctionID).first()
    if auc.number_of_bids == 0:
        messages.warning(request, "No bids yet ... !! ")
        return redirect("auctions", title=auc.title)
    auc.active = False
    auc.save()

    # Determine the winner
    winner_user = get_winner_of_auction(auc)

    return render(request, "auctions/winner.html", {
        "winner_user": winner_user, 
        "auction": auc
    })

@login_required(login_url="/login")
def add_to_watchlist(request, auctionID):
    auc = Auctions.objects.filter(id=auctionID).order_by("-id").first()
    watchlist, created = Watchlist.objects.get_or_create(user=request.user)
    watchlist.auction.add(auc)
    messages.success(request, "✅ Successfully added to Watchlist!")
    return redirect("watchlist_page")


@login_required(login_url="/login")
def watchlist_page(request):
    watchlist, created = Watchlist.objects.get_or_create(user=request.user)
    items = watchlist.auction.all()
    return render(request, "auctions/watchlist.html", {
        "items": items
        })

def remove_from_watchlist(request, auctionID):
    auc = get_object_or_404(Auctions, pk=auctionID)
    watchlist, created = Watchlist.objects.get_or_create(user=request.user)
    if auc in watchlist.auction.all():
        watchlist.auction.remove(auc)
    messages.warning(request, "Successfully removed from Watchlist!")
    return redirect("watchlist_page")


@login_required
def place_bid(request, auction_id):
    auction = get_object_or_404(Auctions, pk=auction_id)

    if request.method == "POST":
        bid_value = float(request.POST.get("bid"))
        if bid_value > auction.current_price:
            # Save new Bids
            Bids.objects.create(
                auction=auction,
                user=request.user,
                amount=bid_value
            )

            # Update number of bids
            auction.number_of_bids += 1

            # Update current price
            auction.current_price = bid_value
            auction.save()
            messages.success(request, "✅ Bid placed successfully!")
        else:
            messages.warning(request, "❌ Bid must be highice.")

        return redirect("auctions", title=auction.title)

    return redirect("auction_detail", auction_id=auction.id)


def add_comment(request, auction_id):
    auction = Auctions.objects.filter(id=auction_id).first()
    if request.method == "POST":
        comment_text = request.POST.get("comment")
        if comment_text:
            Comments.objects.create(
                user=request.user,
                auction=auction,
                comment=comment_text
            )
    messages.success(request, "✅ Your commend added Successfully!")
    
    return redirect("auctions", title=auction.title)