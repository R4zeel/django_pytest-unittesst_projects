from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.not_author_user = User.objects.create(username='Не Автор')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author_id=cls.author.id,
            slug='title'
        )
        cls.author_client = Client()
        cls.not_author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.not_author_client.force_login(cls.not_author_user)

    def test_availability_for_edit_and_delete(self):
        users_statuses = (
            (
                self.author,
                HTTPStatus.OK,
                self.author_client),
            (
                self.not_author_user,
                HTTPStatus.NOT_FOUND,
                self.not_author_client),
        )
        for user, status, client in users_statuses:
            for name in ('notes:detail', 'notes:edit', 'notes:delete'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_base_pages_availability_for_all_users(self):
        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        clients = (
            self.author_client,
            self.not_author_client,
            self.client
        )
        for client in clients:
            for name, args in urls:
                with self.subTest(name=name):
                    url = reverse(name, args=args)
                    response = client.get(url)
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_detail_page_availability_for_all_users(self):
        urls = (
            ('notes:detail', (self.note.slug,)),
        )
        clients = (
            (self.author_client, HTTPStatus.OK),
            (self.not_author_client, HTTPStatus.NOT_FOUND),
            (self.client, HTTPStatus.FOUND)
            # тут проверка на редирект в тесте ниже,
            # хотел проверить соответствие ссылки реддиректа,
            # но пришлось бы использовать if для поиска нужного
            # статуса, поэтому решил оставить отдельным тестом
        )
        for client, status in clients:
            for name, args in urls:
                with self.subTest(name=name):
                    url = reverse(name, args=args)
                    response = client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_non_auth_user_notes_pages_availability(self):
        login_url = reverse('users:login')
        urls = (
            ('notes:success', None),
            ('notes:list', None),
            ('notes:add', None),
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def auth_user_notes_pages_availability(self):
        urls = (
            ('notes:success', None),
            ('notes:list', None),
            ('notes:add', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.author_client.get(url)
                self.assertRedirects(response, HTTPStatus.OK)
