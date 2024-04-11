# tasks.py

from celery import shared_task
import requests
from datetime import datetime, timezone, timedelta
from .models import AltitudeModel, HealthModel, HealthMessage
from django.db import transaction
from django.db.models import Avg


@shared_task
def get_altitude():
    """Celery task for getting satellite altitude.

        Set up to run every 10 seconds to get the updated data. 
        If the date of the request is the same as the last, we will ignore this update.

        Returns:
            altitude_created: boolean 
    """
    url = 'http://nestio.space/api/satellite/data'
    response = requests.get(url)

    # if we don't get a valid response, return
    # we may eventually want to throw an error if we are unable to
    # communicate with the api for a significant period of time
    if (not response.ok):
        return False

    data = response.json()
    if (not data):
        return False

    altitude = data['altitude']
    date = datetime.fromisoformat(data['last_updated'])
    utc_datetime = date.astimezone(timezone.utc)
    with transaction.atomic():
        # if the last entry has the same date stamp, do not add the data twice
        if (AltitudeModel.objects.all().count() > 0):
            last_entry = AltitudeModel.objects.latest('date')
            if (last_entry.date == utc_datetime):
                return False

        # create an object to save the current altitude in the database
        # right now we do not clear the old data
        # but we could use another task to clear out the data
        alt = AltitudeModel.objects.create(
            altitude=altitude, date=utc_datetime)
        alt.save()

    return True


@shared_task
def check_altitude():
    """Celery task for checking average satellite altitude.

      Set up to run every minute. 
      It calculates the past minutes average altitude and updates the HealthModel based on the altitude.

    """
    # get the current time minus a minute
    d = datetime.now(timezone.utc) - timedelta(hours=0, minutes=1)
    with transaction.atomic():
        if (AltitudeModel.objects.all().count() == 0): return

        # get every altitude that was saved in the past minute and average the altitude values
        average_altitude = AltitudeModel.objects.filter(
            date__gte=d).aggregate(Avg('altitude'))['altitude__avg']

        # under 160 km we consider the altitude to be low
        low_altitude = average_altitude < 160

        # we only need one HealthModel object so get it or create it if task is running the first time
        last_warning, created = HealthModel.objects.get_or_create()

        # altitude is low
        if (low_altitude):
            # if it was low last minute, no need to update
            if (last_warning.low_altitude):
                return
            # if it wasn't low before, update the HealthModel
            last_warning.message = HealthMessage.WARNING.value
            last_warning.low_altitude = True
            last_warning.save()
            return

        # current average altitude is not low
        # previous minute had low altitude, we have a special message that is sent
        if (last_warning.low_altitude):
            last_warning.low_altitude = False
            last_warning.message = HealthMessage.SUSTAINED.value
            last_warning.save()
            return

        # if the sustained message was there last minute, we can return to the okay message
        if (last_warning.message == HealthMessage.SUSTAINED.value):
            last_warning.message = HealthMessage.OKAY.value
            last_warning.save()
