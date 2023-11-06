from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import WARNING

from pytils.translit import slugify

User = get_user_model()


class TestNoteCreation(TestCase):
    NOTE_CONTENT = 'test note add'
    NOTE_TITLE = 'test_title'
    NOTE_SLUG = 'testslug'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Мимо Крокодил')
        cls.url = reverse('notes:add', args=None)
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.note_form_data = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_CONTENT,
            'slug': cls.NOTE_SLUG,
            'author': cls.auth_client
        }
        cls.objects_count_with_data = Note.objects.count()

    def test_anonymous_user_cant_create_notes(self):
        self.client.post(self.url, data=self.note_form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, self.objects_count_with_data)

    def test_user_can_create_note(self):
        self.auth_client.post(self.url, data=self.note_form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, self.objects_count_with_data + 1)
        note = Note.objects.get(slug=self.NOTE_SLUG, author=self.author)
        self.assertEqual(note.author, self.author)
        self.assertEqual(note.text, self.NOTE_CONTENT)
        self.assertEqual(note.slug, self.NOTE_SLUG)
        self.assertEqual(note.title, self.NOTE_TITLE)


class TestNoteEditDelete(TestCase):
    NOTE_CONTENT = 'test note add'
    NOTE_TITLE = 'test_title'
    NOTE_SLUG = 'testslug'
    NOTE_UPDATED_TEXT = 'note upd'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.note = Note.objects.create(
            title='pre-build title',
            text=cls.NOTE_CONTENT,
            author_id=cls.author.id,
            slug=cls.NOTE_SLUG
        )
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.edit_form_data = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_UPDATED_TEXT,
            'slug': cls.NOTE_SLUG,
        }
        cls.objects_count_with_data = Note.objects.count()

    def test_author_can_delete_note(self):
        self.author_client.delete(self.delete_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, self.objects_count_with_data - 1)

    def test_user_cant_delete_note_of_another_user(self):
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, self.objects_count_with_data)

    def test_author_can_edit_note(self):
        self.author_client.post(
            self.edit_url,
            data=self.edit_form_data
        )
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_UPDATED_TEXT)

    def test_user_cant_edit_note_of_another_user(self):
        self.reader_client.post(
            self.edit_url,
            data=self.edit_form_data
        )
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_CONTENT)

    def test_cannot_create_notes_with_same_slug(self):
        url = reverse('notes:add')
        response = self.author_client.post(url, data=self.edit_form_data)
        notes_count = Note.objects.count()
        self.assertFormError(
            response,
            'form',
            'slug',
            errors=(self.edit_form_data['slug'] + WARNING)
        )
        self.assertEqual(notes_count, self.objects_count_with_data)

    def test_slug_auto_fill(self):
        url = reverse('notes:add')
        self.edit_form_data.pop('slug')
        response = self.author_client.post(url, data=self.edit_form_data)
        self.assertRedirects(response, reverse('notes:success'))
        note_count = Note.objects.count()
        self.assertEqual(note_count, self.objects_count_with_data + 1)
        new_note = Note.objects.get(
            title=self.edit_form_data['title'],
            author=self.author
        )
        expected_slug = slugify(self.edit_form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)
