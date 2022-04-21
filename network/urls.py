
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    path("profile/<int:user_id>", views.profile, name="profile"),
    path("profile/follow/<int:user_id>", views.follow, name="follow"),

    path("posts", views.compose, name="compose-post"),
    path("posts/<int:post_id>", views.posts, name="post"),
    path("posts/<int:post_id>/comments", views.add_comment, name="comment"),

    path("likes/<int:post_id>", views.like_the_post, name="like"),

    path("following", views.following_posts, name="following-posts"),
    path("profile/likes/<int:post_id>", views.like_the_post, name="like"),

]
