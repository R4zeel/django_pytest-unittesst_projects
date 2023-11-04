from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model


User = get_user_model()


class TestAddNotePage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.auth_user = User.objects.create(username='User')
        cls.add_url = reverse('notes:add', args=None)

    def test_anonymous_client_has_no_form(self):
        response = self.client.get(self.add_url)
        self.assertEqual(response.context, None)

    def test_authorized_client_has_form(self):
        self.client.force_login(self.auth_user)
        response = self.client.get(self.add_url)
        self.assertIn('form', response.context)
