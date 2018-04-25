from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from enum import Enum

class Color(Enum):
    YELLOW = 0
    RED = 1
    BLUE = 2
    GREEN = 3
    NONE = -1


class Type(Enum):
    NORMAL = 0
    PULL2 = 1
    PULL4 = 2
    CHANGE_COLOR = 3
    LOSE_TURN = 4
    RETOUR = 5


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    wins = models.PositiveIntegerField(default=0)
    
    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save() 


class Game(models.Model):
    STATE_CHOICES = (
        ('PENDING', 0),
        ('RUNNING', 1),
        ('FINISHED', 2),
    )
    name = models.CharField(max_length=25, blank=True)
    players = models.ManyToManyField(User, blank=True, related_name="players_set")
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="creator")
    state = models.IntegerField(choices=STATE_CHOICES, default=0)


