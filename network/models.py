from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models


class User(AbstractUser):
    image = models.ImageField(null=True, blank=True, default='default.png')
    location = models.CharField(max_length=100, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)


class UserFollowing(models.Model):
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='following')
    following_user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='followers')

    def __str__(self):
        return f"User {self.user_id} is following {self.following_user_id}"


class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now=True)
    likes = models.IntegerField(default=0, null=True, blank=True)
    reposts = models.IntegerField(default=0, null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']

    def serialize(self):
        return {
            "user": self.user.username,
            "content": self.content,
            "timestamp": self.timestamp.strftime("%b %d %Y, %I:%M %p"),
            'likes': self.likes,
            'reposts': self.reposts,
        }

    def __str__(self):
        return f"{self.user} posted on {self.timestamp}"


class UserLikes(models.Model):
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='posts_likes')

    def __str__(self):
        return f"User {self.user_id} likes post {self.post_id.id}"


class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)

    def serialize(self):
        return {
            "user": self.user.username,
            "content": self.content,
            "timestamp": self.timestamp.strftime("%b %d %Y, %I:%M %p"),
        }


