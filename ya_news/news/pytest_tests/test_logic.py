from pytest_django.asserts import assertRedirects
from django.urls import reverse

from news.models import News, Comment

from http import HTTPStatus

import pytest


def test_user_can_create_comment(author_client, author, form_data, news):
    url = reverse('news:detail', args=(news.pk,))
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']
    assert new_comment.author == author


@pytest.mark.django_db
def test_anonymous_user_cant_create_note(client, form_data, news):
    url = reverse('news:detail', args=(news.pk,))
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_author_can_edit_comment(author_client, form_data, comment):
    url = reverse('news:edit', args=(comment.pk,))
    success_url = reverse('news:detail', args=(comment.news_id,))
    response = author_client.post(url, form_data)
    assertRedirects(response, f'{success_url}#comments')
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_other_user_cant_edit_note(admin_client, form_data, comment):
    url = reverse('news:edit', args=(comment.pk,))
    response = admin_client.post(url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text


def test_author_can_delete_note(author_client, comment, comments_pk_for_args):
    url = reverse('news:delete', args=(comments_pk_for_args,))
    success_url = reverse('news:detail', args=(comment.news_id,))
    response = author_client.post(url)
    assertRedirects(response, f'{success_url}#comments')
    assert Comment.objects.count() == 0


def test_other_user_cant_delete_note(admin_client, form_data, comments_pk_for_args):
    url = reverse('news:delete', args=(comments_pk_for_args,))
    response = admin_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1