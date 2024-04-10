from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
import json
from unittest.mock import patch, Mock
from zoneinfo import ZoneInfo
from ..models import AltitudeModel

import datetime


class EmptyStatsTestCase(APITestCase):
    def test_empty_stats(self):
        """
        Check that stats are null when there are no AltitudeModel objects
        """
        # url = reverse('stats/')
        response = self.client.get('/stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(json.loads(response.content), {
                             "minimum": None, "maximum": None, "average": None})


class NewDate(datetime.datetime):
    @classmethod
    def now(cls, tz):
        return cls(2024, 4, 6, 1, 20, tzinfo=ZoneInfo("UTC"))


datetime.datetime = NewDate


class StatsTestCase(APITestCase):
    def setUp(self):
        AltitudeModel.objects.create(altitude=150, date=NewDate(
            2024, 4, 6, 1, 22, tzinfo=ZoneInfo("UTC")))

    def test_empty_stats(self):
        """
        Check that stats are null when there are no AltitudeModel objects
        """
        # url = reverse('stats/')
        response = self.client.get('/stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(json.loads(response.content), {
                             "minimum": 150, "maximum": 150, "average": 150})
