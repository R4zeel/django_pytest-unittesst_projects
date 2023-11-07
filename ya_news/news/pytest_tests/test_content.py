import pytest

from django.urls import reverse
from django.conf import settings

from news.forms import CommentForm


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:detail', pytest.lazy_fixture('comments_pk_for_args')),
    )
)
def test_pages_contains_form(author_client, name, args):
    url = reverse(name, args=(args,))
    response = author_client.get(url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('comments_pk_for_args')),
    )
)
def test_anonymous_client_has_no_form(client, name, args):
    url = reverse(name, args=(args,))
    response = client.get(url)
    assert response.context is None


@pytest.mark.parametrize(
    'client',
    (
        (pytest.lazy_fixture('admin_client'),)
    )
)
def test_news_count(client, multiple_news):
    url = reverse('news:home')
    response = client.get(url)
    assert 'news_feed' in response.context
    object_list = response.context['news_feed']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.parametrize(
    'client',
    (
        (pytest.lazy_fixture('admin_client'),)
    )
)
def test_news_order(client, multiple_news):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['news_feed']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.parametrize(
    'client',
    (
        (pytest.lazy_fixture('admin_client'),)
    )
)
def test_comments_order(client, multiple_comments, news):
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    for index in range(len(all_comments) - 1):
        assert (all_comments[index].created
                < all_comments[index + 1].created)
