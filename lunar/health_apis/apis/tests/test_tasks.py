from unittest.mock import patch, Mock
from django.test import TestCase
from ..tasks import get_altitude, check_altitude
from ..models import AltitudeModel, HealthMessage, HealthModel
from datetime import datetime, timezone
from ..conftest import NewDate

import pytest

class MockResponseClass:
    def __init__(self, ok):
        self.ok = ok
        
not_okay_response = MockResponseClass(False)
not_okay_response.json = Mock(return_value=None)

empty_json_response = MockResponseClass(True)
empty_json_response.json = Mock(return_value=None)

standard_response = MockResponseClass(True)
date = datetime(2024, 4, 10, 2, 33, tzinfo=timezone.utc)
print(date.isoformat())
standard_response.json = Mock(return_value={ 'altitude': 165, 'last_updated': date.isoformat()})

@pytest.mark.celery(result_backend='redis://')
class test_get_altitude(TestCase): 
    @patch('requests.get', Mock(return_value=not_okay_response))  
    def test_response_not_ok(self):
        """
        Check that an object is not created when there is a non okay response
        """
        created = get_altitude()
        self.assertEqual(created, False)
        not_okay_response.json.assert_not_called()
        self.assertEqual(AltitudeModel.objects.all().count(), 0)

    @patch('requests.get', Mock(return_value=empty_json_response))  
    def test_empty_json_response(self):
        """
        Check that an object is not created when json is empty
        """
        created = get_altitude()
        self.assertEqual(created, False)
        empty_json_response.json.assert_called()
        self.assertEqual(AltitudeModel.objects.all().count(), 0)

    @patch('requests.get', Mock(return_value=standard_response))  
    def test_creating_altitude_object(self):
        """
        Check that an object is created 
        """
        created = get_altitude()
        self.assertEqual(created, True)
        standard_response.json.assert_called()
        self.assertEqual(AltitudeModel.objects.all().count(), 1)
        altitudeObj = AltitudeModel.objects.get()
        self.assertEqual(altitudeObj.altitude, 165)
        self.assertEqual(altitudeObj.date, date)

    @patch('requests.get', Mock(return_value=standard_response))  
    def test_shared_date(self):
        """
        Check that an object is not created when there is an object that has the same date
        """
        AltitudeModel.objects.create(altitude=125, date=date)
        created = get_altitude()
        self.assertEqual(created, False)
        standard_response.json.assert_called()
        self.assertEqual(AltitudeModel.objects.all().count(), 1)
    
@patch('apis.tasks.datetime', NewDate)
@pytest.mark.celery(result_backend='redis://')
class test_check_low_altitude(TestCase): 
    def setUp(self):
        # average over past minute should be 143.75 -- low altitude
        AltitudeModel.objects.create(altitude=150, date=NewDate(
            2024, 4, 6, 1, 19, tzinfo=timezone.utc))
        AltitudeModel.objects.create(altitude=200, date=NewDate(
            2024, 4, 6, 1, 20, tzinfo=timezone.utc))
        AltitudeModel.objects.create(altitude=100, date=NewDate(
            2024, 4, 6, 1, 19, tzinfo=timezone.utc))
        AltitudeModel.objects.create(altitude=125, date=NewDate(
            2024, 4, 6, 1, 20, tzinfo=timezone.utc))
        AltitudeModel.objects.create(altitude=90, date=NewDate(
            2024, 4, 6, 0, 34, tzinfo=timezone.utc))
        AltitudeModel.objects.create(altitude=260, date=NewDate(
            2024, 4, 6, 0, 20, tzinfo=timezone.utc))

    def test_creates_health_model(self):
        """
        Check that HealthModel object is created when one doesn't exist
        """
        self.assertEqual(HealthModel.objects.all().count(), 0)
        check_altitude()
        self.assertEqual(HealthModel.objects.all().count(), 1)
        healthObj = HealthModel.objects.get()
        self.assertEqual(healthObj.low_altitude, True)
        self.assertEqual(healthObj.message, HealthMessage.WARNING.value)

    def test_updates_health_model(self):
        """
        Check that HealthModel is updated when low altitude average occurs
        """
        HealthModel.objects.create(low_altitude=False, message=HealthMessage.OKAY.value)
        check_altitude()
        self.assertEqual(HealthModel.objects.all().count(), 1)
        healthObj = HealthModel.objects.get()
        self.assertEqual(healthObj.low_altitude, True)
        self.assertEqual(healthObj.message, HealthMessage.WARNING.value)

@patch('apis.tasks.datetime', NewDate)
@pytest.mark.celery(result_backend='redis://')
class test_check_high_altitude(TestCase): 
    def setUp(self):
        # average over past minute should be 182.5 -- high altitude
        AltitudeModel.objects.create(altitude=170, date=NewDate(
            2024, 4, 6, 1, 19, tzinfo=timezone.utc))
        AltitudeModel.objects.create(altitude=200, date=NewDate(
            2024, 4, 6, 1, 20, tzinfo=timezone.utc))
        AltitudeModel.objects.create(altitude=210, date=NewDate(
            2024, 4, 6, 1, 19, tzinfo=timezone.utc))
        AltitudeModel.objects.create(altitude=150, date=NewDate(
            2024, 4, 6, 1, 20, tzinfo=timezone.utc))
        # these two objects are out of range
        AltitudeModel.objects.create(altitude=90, date=NewDate(
            2024, 4, 6, 0, 34, tzinfo=timezone.utc))
        AltitudeModel.objects.create(altitude=80, date=NewDate(
            2024, 4, 6, 0, 20, tzinfo=timezone.utc))

    def test_creates_health_model(self):
        """
        Check that health model is created when one doesn't exist
        """
        self.assertEqual(HealthModel.objects.all().count(), 0)
        check_altitude()
        self.assertEqual(HealthModel.objects.all().count(), 1)
        healthObj = HealthModel.objects.get()
        self.assertEqual(healthObj.low_altitude, False)
        self.assertEqual(healthObj.message, HealthMessage.OKAY.value)

    def test_updates_health_model(self):
        """
        Check that HealthModel is updated when previous minute had low altitude
        """
        HealthModel.objects.create(low_altitude=True, message=HealthMessage.WARNING.value)
        check_altitude()
        self.assertEqual(HealthModel.objects.all().count(), 1)
        healthObj = HealthModel.objects.get()
        self.assertEqual(healthObj.low_altitude, False)
        self.assertEqual(healthObj.message, HealthMessage.SUSTAINED.value)

    def test_updates_health_model(self):
        """
        Check that HealthModel is updated when previous minute had the sustained message
        """
        HealthModel.objects.create(low_altitude=False, message=HealthMessage.SUSTAINED.value)
        check_altitude()
        self.assertEqual(HealthModel.objects.all().count(), 1)
        healthObj = HealthModel.objects.get()
        self.assertEqual(healthObj.low_altitude, False)
        self.assertEqual(healthObj.message, HealthMessage.OKAY.value)
