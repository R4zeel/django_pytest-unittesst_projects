from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.not_author_user = User.objects.create(username='Не Автор')
        cls.note = Note.objects.create(title='Заголовок', text='Текст', author_id=cls.author.id, slug='title')

    def test_availability_for_edit_and_delete(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.not_author_user, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('notes:edit', 'notes:delete'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_pages_availability(self):
        urls = (
            ('notes:home', None),
            ('notes:detail', (self.note.slug,)),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                if name == 'notes:detail':
                    self.assertEqual(response.status_code, HTTPStatus.FOUND)
                    continue
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        for name in ('notes:edit', 'notes:delete'):
            with self.subTest(name=name):
                url = reverse(name, args=(self.note.slug,))
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_add_note_availability(self):
        login_url = reverse('users:login')
        url = reverse('notes:add', args=None)
        redirect_url = f'{login_url}?next={url}'
        response = self.client.get(url)
        self.assertRedirects(response, redirect_url)
