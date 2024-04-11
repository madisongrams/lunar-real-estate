from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from django.http import HttpResponse, JsonResponse
from .models import AltitudeModel, HealthModel
from django.db.models import Avg, Max, Min
from datetime import datetime, timedelta, timezone
from django.db import transaction


def _get_stats():
    """Helper function to get the average, max and min altitudes over the past five minutes.

    Returns:
        stats: A dict containing minimum, maximum, and average altitudes over past 5 minutes as floats. Values will be None if no data exists.
    """
    d = datetime.now(timezone.utc) - timedelta(hours=0, minutes=5)

    stats_aggregate = AltitudeModel.objects.filter(date__gte=d).aggregate(
        Avg('altitude'), Max('altitude'), Min('altitude'))

    stats = {
        'minimum': stats_aggregate['altitude__min'],
        'maximum': stats_aggregate['altitude__max'],
        'average': stats_aggregate['altitude__avg']
    }
    return stats


@transaction.atomic
@api_view(['GET'])
def get_stats(request):
    """GET endpoint for /stats/ that returns statistics about recent altitude information as a JsonResponse
    """
    stats = _get_stats()
    return JsonResponse(stats)


@transaction.atomic
@api_view(['GET'])
def get_health(request):
    """GET endpoint for /health/ that returns a message regarding recent altitude levels.
    """
    try:
        health = HealthModel.objects.get()
        return HttpResponse(health.message)
    except HealthModel.DoesNotExist:
        return Response(status=status.HTTP_204_NO_CONTENT)
