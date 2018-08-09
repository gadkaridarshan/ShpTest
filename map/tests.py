from django.test import TestCase

import json
import geocoder
from datetime import datetime

# Create your tests here.
from map.models import Coordinate

class CoordinateTestCase(TestCase):

    def test_drop_db(self):
        Coordinate.objects.all().delete()
        elementNb = Coordinate.objects.filter().count()
        self.assertEqual(elementNb,0)

    def test_reverse_geocoding_true(self):
        lat = -26.5982647
        lng = 120.4536475
        g = geocoder.google([lat, lng], method='reverse')
        tmpCoordinate = g.json
        self.assertEqual(tmpCoordinate['ok'], True)

    def test_reverse_geocoding_false(self):
        lat = -37
        lng = 125
        g = geocoder.google([lat, lng], method='reverse')
        tmpCoordinate = g.json
        self.assertEqual(tmpCoordinate['ok'], False)
