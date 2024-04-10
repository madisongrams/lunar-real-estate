from django.db import models
from enum import Enum

class HealthMessage(Enum):
  WARNING = "WARNING: RAPID ORBITAL DECAY IMMINENT"
  SUSTAINED = "Sustained Low Earth Orbit Resumed"
  OKAY = "Altitude is A-OK"

class HealthModel(models.Model):
  low_altitude = models.BooleanField(default=False)
  message = models.TextField(default=HealthMessage.OKAY.value)

class AltitudeModel(models.Model):
  altitude = models.FloatField()
  date = models.DateTimeField()
