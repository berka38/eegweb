# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

# Blance = models.IntegerField(_('Balance'), default=0)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.IntegerField(default=0)  # Varsayılan 0 olarak tanımlandı.

    def __str__(self):
        return f"{self.user.username} - Profile"

# Signals ile her yeni kullanıcı oluşturulduğunda profil de otomatik oluşturulsun
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()