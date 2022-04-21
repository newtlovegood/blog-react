from django.contrib import admin
from django.conf import settings
from .models import User, Post, Comment, UserFollowing, UserLikes

admin.site.register(User)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(UserFollowing)
admin.site.register(UserLikes)
