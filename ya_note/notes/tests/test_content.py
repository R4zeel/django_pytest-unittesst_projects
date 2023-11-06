from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestAddNotePage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='User')
        cls.note = Note.objects.create(
            title='pre-build title',
            text='test text',
            author_id=cls.author.id,
            slug='testslug'
        )
        cls.not_author = User.objects.create(username='Other User')
        cls.add_url = reverse('notes:add', args=None)
        cls.author_client = Client()
        cls.not_author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.not_author_client.force_login(cls.not_author)

    def test_note_in_list_for_author(self):
        url = reverse('notes:list')
        response = self.author_client.get(url)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_note_not_in_list_for_another_user(self):
        url = reverse('notes:list')
        response = self.not_author_client.get(url)
        object_list = response.context['object_list']
        self.assertNotIn(self.note, object_list)

    def test_anonymous_client_has_no_form(self):
        response = self.client.get(self.add_url)
        self.assertEqual(response.context, None)

    def test_authorized_client_has_forms(self):
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,))
        )
        for name, args in urls:
            with self.subTest(user=self.author_client, name=name):
                url = reverse(name, args=args)
                response = self.author_client.get(url)
                self.assertEqual(
                    isinstance(response.context['form'], NoteForm),
                    True
                )
                self.assertIn('form', response.context)
