from django.contrib import admin

from .models import User, Auctions, Comments
# Register your models here.


admin.site.register(User)
admin.site.register(Auctions)
admin.site.register(Comments)