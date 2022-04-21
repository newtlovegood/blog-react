from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core.paginator import Paginator
from django.shortcuts import render
from django.urls import reverse

from .models import User, Post, UserFollowing, UserLikes, Comment

import json
import operator


def index(request):
    posts = Post.objects.all()
    p = Paginator(posts, 10)
    page_number = request.GET.get('page', 1)
    page_obj = p.get_page(page_number)

    liked_posts = liked_by_current_user(request.user, posts)

    context = {
        'page_obj': page_obj,
        'liked_by_current_user': liked_posts
    }
    return render(request, "network/index.html", context)


@login_required
def compose(request):
    if request.method != 'POST':
        return JsonResponse({"error": "POST request required."}, status=400)

    data = json.loads(request.body)
    post = Post.objects.create(content=data.get('content'),
                               user=request.user)

    return JsonResponse({"message": "Post created successfully.",
                         "post_id": post.id}, status=201)


def posts(request, post_id):
    # Query for the post
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Message does not exists"}, status=404)

    # Return post content
    if request.method == "GET":
        return JsonResponse(post.serialize())

    if request.method == "PUT" and request.user.id == post.user_id:
        data = json.loads(request.body)
        if data.get("content") is not None:
            post.content = data["content"]
        post.save()
        return JsonResponse(post.serialize())
    # Posts must be via GET or PUT

    else:
        return JsonResponse({
            "error": "GET or PUT request required."
        }, status=400)


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


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
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


def profile(request, user_id):
    user_profile = User.objects.get(id=user_id)
    posts = Post.objects.filter(user_id=user_id)
    following = user_profile.following.all()
    followers = user_profile.followers.all()

    try:
        UserFollowing.objects.get(user_id=request.user.id, following_user_id=user_id)
        current_user_followed_by = True
    except UserFollowing.DoesNotExist:
        current_user_followed_by = False

    context = {
        'profile': user_profile,
        'posts': posts,
        'following': following,
        'followers': followers,
        'current_user_followed_by': current_user_followed_by,
    }
    return render(request, 'network/profile.html', context)


def follow(request, user_id):
    if user_id == request.user.id:
        return JsonResponse({'error': 'You cannot follow yourself'}, status=400)

    link, created = UserFollowing.objects.get_or_create(user_id_id=request.user.id,
                                                        following_user_id_id=user_id)
    # update following count
    followers_users = User.objects.get(id=user_id).followers.count()

    if request.method == 'GET':
        if created:
            return JsonResponse({'message': f'User {user_id} is followed by {request.user}',
                                 'unfollowed': False,
                                 'followers': followers_users}, status=201)
        else:
            # already following -> unfollow
            link.delete()
            return JsonResponse({'message': f'User {user_id} was unfollowed ',
                                 'unfollowed': True,
                                 'followers': followers_users-1}, status=201)


@login_required
def following_posts(request):
    current_user = User.objects.get(id=request.user.id)
    following = current_user.following.all()
    posts = []
    for pair in following:
        posts += list(Post.objects.filter(user_id=pair.following_user_id))
    ordered = sorted(posts, key=operator.attrgetter('timestamp'), reverse=True)

    p = Paginator(ordered, 10)
    page_number = request.GET.get('page', 1)
    page_obj = p.get_page(page_number)

    # liked by current user - For icon diplsay
    liked_posts = liked_by_current_user(request.user, ordered)

    context = {
        'page_obj': page_obj,
        'liked_by_current_user': liked_posts,
    }
    return render(request, "network/index.html", context)


@login_required
def like_the_post(request, post_id):

    like, created = UserLikes.objects.get_or_create(user_id_id=request.user.id, post_id_id=post_id)

    post_likes = Post.objects.get(id=post_id).posts_likes.count()

    if request.method == 'GET':
        if created:
            return JsonResponse({'likes': post_likes,
                                 'created': True}, status=201)
        else:
            # already following -> unfollow
            like.delete()
            return JsonResponse({'likes': post_likes - 1,
                                 'created': False}, status=201)


def liked_by_current_user(current_user, posts):
    liked_posts = []

    for post in posts:
        post_id = post.id

        try:
            UserLikes.objects.get(user_id=current_user.id, post_id=post_id)
            liked_posts.append(post_id)
        except UserLikes.DoesNotExist:
            pass

    return liked_posts


@login_required
def add_comment(request, post_id):

    if request.method == 'POST':
        data = json.loads(request.body)

        comment = Comment.objects.create(user_id=request.user.id,
                                         post_id=post_id,
                                         content=data.get("content"))

        return JsonResponse({"user": comment.user,
                             "message": comment.content,
                             "timestamp": comment.timestamp}, status=201)

    elif request.method == 'GET':

        comments = []
        queryset = Comment.objects.filter(post_id=post_id)
        for comment in queryset:
            comments.append(comment.serialize())
        return JsonResponse({"comments": comments})

