from django.db import models

class Coordinate(models.Model):
	Unique_ID = models.CharField(max_length=128,null=True, blank=True)
	Address = models.CharField(max_length=500,null=True, blank=True)
	Latitude = models.CharField(max_length=32,null=True, blank=True)
	Longitude = models.CharField(max_length=32,null=True, blank=True)
	Creation = models.DateTimeField(auto_now_add=True, blank=True)
