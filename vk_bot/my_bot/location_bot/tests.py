"""Test here"""

from django.test import TestCase, SimpleTestCase
from django.urls import reverse, resolve
from .views import index, cart_generate


class TestUrls(TestCase):
    """Urls tests"""
    def test_cart_generate(self):
        """Test url name cartGenerate"""
        url = reverse('cartGenerate')
        self.assertEquals(resolve(url).func, cart_generate)
