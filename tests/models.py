
from django.db import models

class Author(models.Model):

    name = models.CharField(max_length=128)

class Book(models.Model):

    author = models.ForeignKey(Author)
    date = models.DateField()
    title = models.CharField(max_length=128)
