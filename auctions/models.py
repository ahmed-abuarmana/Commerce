from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

# ==========================================================================================================

class Auctions(models.Model):
    id = models.AutoField(primary_key=True)
    createdBy = models.ForeignKey(User, on_delete=models.CASCADE, related_name="auctions")
    title = models.CharField(max_length=20)
    description = models.CharField(max_length=100)
    startingBid = models.FloatField()
    current_price = models.FloatField()
    imageURL = models.CharField(blank=True)
    category = models.CharField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    number_of_bids = models.IntegerField(default=0)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title}"
    
    def save(self, *args, **kwargs):
        if not self.current_price:
            self.current_price = self.startingBid
        super().save(*args, **kwargs)

# ==========================================================================================================

class Bids(models.Model):
    auction = models.ForeignKey("Auctions", on_delete=models.CASCADE, related_name="bids")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_bids")
    amount = models.FloatField(default=0)

class Comments(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    auction = models.ForeignKey("Auctions", on_delete=models.CASCADE)
    comment = models.TextField()

class Watchlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="watchlist")
    auction = models.ManyToManyField(Auctions, related_name="watchlisted_in", blank=True)

    def __str__(self):
        return f"{self.user.username}'s Watchlist"