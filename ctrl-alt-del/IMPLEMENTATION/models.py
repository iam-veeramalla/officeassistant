from __future__ import unicode_literals
from django.db import models


class Post(models.Model):
    match1 = models.CharField(max_length=255)
    match2 = models.CharField(max_length=255)
    date = models.CharField(max_length=255)


class Selection(models.Model):
    user = models.CharField(max_length=255)
    match1 = models.CharField(max_length=255)
    match2 = models.CharField(max_length=255)
    date = models.CharField(max_length=255)
    choice1 = models.CharField(max_length=255)
    choice2 = models.CharField(max_length=255)
    points = models.IntegerField()
