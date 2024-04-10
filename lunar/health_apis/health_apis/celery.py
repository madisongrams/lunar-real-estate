# celery.py

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from datetime import timedelta
from django.db.models import Avg, Max, Min

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'health_apis.settings')

app = Celery('health_apis')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# # Load task modules from all registered Django app configs.
app.autodiscover_tasks()

app.conf.timezone = 'UTC'

app.conf.beat_schedule = {
  'get-altitude': {
    'task': 'apis.tasks.get_altitude',
    'schedule': 10.0,
  },
  'check-altitude': {
    'task': 'apis.tasks.check_altitude',
    'schedule': 60.0,
  },
}
