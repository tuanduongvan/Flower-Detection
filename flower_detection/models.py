from django.db import models
from django.utils.timezone import now

class Flower(models.Model):
    name = models.CharField(max_length=255)
    fullname = models.CharField(max_length=255, null=True, blank=True)
    image = models.CharField(max_length=255, null=True, blank=True)
    scientific_name = models.CharField(max_length=255)
    characteristic = models.TextField(null=True, blank=True)
    residence = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class SearchHistory(models.Model):
    id = models.AutoField(primary_key=True) 
    linkflower = models.TextField(max_length=255, null=True, blank=True)
    image = models.TextField(max_length=255, null=True, blank=True)  # Ảnh được lưu trữ (nếu có)
    time = models.DateField(default=now)  # Thời gian tìm kiếm, mặc định là thời điểm hiện tại

    def __str__(self):
        return f"Search for {self.id} at {self.time}"

    def define(self, ht):
        self.id = ht.id
        self.linkflower = ht.linkflower
        self.image = ht.image
        self.time = ht.time
        return self
# Create your models here.
