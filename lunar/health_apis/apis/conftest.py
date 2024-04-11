# conftest.py
from rest_framework.test import APIClient
import pytest
from datetime import timezone
import datetime

@pytest.fixture
def api_client():
  return APIClient

class NewDate(datetime.datetime):
    @classmethod
    def now(cls, tz):
        return cls(2024, 4, 6, 1, 20, tzinfo=timezone.utc)
