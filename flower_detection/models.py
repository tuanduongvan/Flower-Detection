from django.db import models

class Flower(models.Model):
    name = models.CharField(max_length=255)
    fullname = models.CharField(max_length=255, null=True, blank=True)
    image = models.CharField(max_length=255, null=True, blank=True)
    scientific_name = models.CharField(max_length=255)
    characteristic = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

# Create your models here.
