from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse, JsonResponse
from .models import AltitudeModel, HealthModel
from django.db.models import Avg, Max, Min
from datetime import datetime, timedelta
from django.db import transaction

@transaction.atomic
@api_view(['GET'])
def get_stats(request):

  d = datetime.now() - timedelta(hours=0, minutes=5)

  stats_aggregate = AltitudeModel.objects.filter(date__gt=d).aggregate(Avg('altitude'), Max('altitude'), Min('altitude'))
  print(stats_aggregate)
  
  stats_d = {
    'minimum': stats_aggregate['altitude__min'],
    'maximum': stats_aggregate['altitude__max'],
    'average': stats_aggregate['altitude__avg']
  }
  return JsonResponse(stats_d)

@transaction.atomic
@api_view(['GET'])
def get_health(request):
  try:
    health = HealthModel.objects.get()
    return HttpResponse(health.message)
  except HealthModel.DoesNotExist:
    return HttpResponse()

  
  
