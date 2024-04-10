# tasks.py

from celery import shared_task
from time import sleep
import requests
import json
from datetime import datetime, timezone, timedelta
from .models import AltitudeModel, HealthModel, HealthMessage
from zoneinfo import ZoneInfo
from django.db import transaction
from django.db.models import Avg, Max, Min

@shared_task
def get_altitude():
  url = 'http://nestio.space/api/satellite/data'
  response = requests.get(url)

  if (not response.ok): return

  data = response.json()
  if (not data): return

  # data = json.loads(data)
  altitude = data['altitude']
  date = datetime.fromisoformat(data['last_updated'])
  utc_datetime = date.astimezone(ZoneInfo("UTC"))

  print(altitude, date)

  with transaction.atomic():
    alt = AltitudeModel(altitude=altitude, date=utc_datetime)
    alt.save()

@shared_task
def check_altitude():
  d = datetime.now(timezone.utc) - timedelta(hours=0, minutes=1)
  with transaction.atomic():
    average_altitude = AltitudeModel.objects.filter(date__gt=d).aggregate(Avg('altitude'))['altitude__avg']

    low_altitude = average_altitude < 160
    last_warning, created = HealthModel.objects.get_or_create()

    if (low_altitude): 
      if (last_warning.low_altitude): return
      last_warning.message = HealthMessage.WARNING.value
      last_warning.low_altitude = True
      last_warning.save()
      return

    # last minute was low altitude, but now it is 
    if (last_warning.low_altitude):
      last_warning.low_altitude = False
      last_warning.message = HealthMessage.SUSTAINED.value
      last_warning.save()
      return
    
    if (last_warning.message == HealthMessage.SUSTAINED.value):
      last_warning.message = HealthMessage.OKAY.value
      last_warning.save()
