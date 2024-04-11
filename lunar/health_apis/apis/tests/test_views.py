from rest_framework import status
from rest_framework.test import APITestCase
import json
from zoneinfo import ZoneInfo
from ..models import AltitudeModel, HealthMessage, HealthModel

import datetime


class EmptyStatsTestCase(APITestCase):
    def test_empty_stats(self):
        """
        Check that stats are null when there are no AltitudeModel objects
        """
        response = self.client.get('/stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(json.loads(response.content), {
                             "minimum": None, "maximum": None, "average": None})


class NewDate(datetime.datetime):
    @classmethod
    def now(cls, tz):
        return cls(2024, 4, 6, 1, 20, tzinfo=ZoneInfo("UTC"))


datetime.datetime = NewDate


class SingleStatsTestCase(APITestCase):
    def setUp(self):
        AltitudeModel.objects.create(altitude=150, date=NewDate(
            2024, 4, 6, 1, 22, tzinfo=ZoneInfo("UTC")))

    def test_empty_stats(self):
        """
        Check that stats are correct with one entry
        """
        response = self.client.get('/stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(json.loads(response.content), {
                             "minimum": 150, "maximum": 150, "average": 150})


class MixedStatsTestCase(APITestCase):
    def setUp(self):
        AltitudeModel.objects.create(altitude=150, date=NewDate(
            2024, 4, 6, 1, 22, tzinfo=ZoneInfo("UTC")))
        AltitudeModel.objects.create(altitude=200, date=NewDate(
            2024, 4, 6, 1, 23, tzinfo=ZoneInfo("UTC")))
        AltitudeModel.objects.create(altitude=100, date=NewDate(
            2024, 4, 6, 1, 21, tzinfo=ZoneInfo("UTC")))
        AltitudeModel.objects.create(altitude=125, date=NewDate(
            2024, 4, 6, 1, 22, tzinfo=ZoneInfo("UTC")))
        AltitudeModel.objects.create(altitude=90, date=NewDate(
            2024, 4, 6, 0, 34, tzinfo=ZoneInfo("UTC")))
        AltitudeModel.objects.create(altitude=260, date=NewDate(
            2024, 4, 6, 0, 20, tzinfo=ZoneInfo("UTC")))

    def test_empty_stats(self):
        """
        Check that stats are correct with multiple entries both in and out of the five minute range
        """
        response = self.client.get('/stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(json.loads(response.content), {
                             "minimum": 100, "maximum": 200, "average": 143.75})


class EmptyHealthTestCase(APITestCase):
    def test_empty_health(self):
        """
        Check that 204 status returned when there is no data.
        """
        response = self.client.get('/health/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class PopulatedHealthTestCase(APITestCase):
    def setUp(self):
        HealthModel.objects.create(
            low_altitude=True, message=HealthMessage.WARNING.value)

    def test_empty_health(self):
        """
        Check that message is sent in response when data exists.
        """
        response = self.client.get('/health/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content.decode(),
                         HealthMessage.WARNING.value)
