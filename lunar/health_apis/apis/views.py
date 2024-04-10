from rest_framework.decorators import api_view
from django.http import HttpResponse, JsonResponse
from .models import AltitudeModel, HealthModel
from django.db.models import Avg, Max, Min
from datetime import datetime, timedelta, timezone
from django.db import transaction


def _get_stats():
  d = datetime.now(timezone.utc) - timedelta(hours=0, minutes=5)

  stats_aggregate = AltitudeModel.objects.filter(date__gt=d).aggregate(Avg('altitude'), Max('altitude'), Min('altitude'))
  
  stats = {
    'minimum': stats_aggregate['altitude__min'],
    'maximum': stats_aggregate['altitude__max'],
    'average': stats_aggregate['altitude__avg']
  }
  return stats

@transaction.atomic
@api_view(['GET'])
def get_stats(request):
  stats = _get_stats()
  return JsonResponse(stats)

@transaction.atomic
@api_view(['GET'])
def get_health(request):
  try:
    health = HealthModel.objects.get()
    return HttpResponse(health.message)
  except HealthModel.DoesNotExist:
    return HttpResponse()

  
  
