import pytest
from datetime import datetime, timedelta, date
from random import randint

from django.conf import settings
from django.utils import timezone

from news.models import News, Comment


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def news(author):
    news = News.objects.create(
        title='Заголовок',
        text='Текст заметки',
    )
    return news


@pytest.fixture
def multiple_news(news):
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=date(today.year, today.month, randint(1, 28))
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    test_news = News(
            title='А нОвость', 
            text='А пРосто текст',
            date=(datetime(year=2021, month=1, day=1))
        )
    all_news.append(test_news)
    return News.objects.bulk_create(all_news)


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        text='Текст заметки',
        author=author,
    )
    return comment


@pytest.fixture
def multiple_comments(author, news):
    now = timezone.now()
    comments = [
        Comment.objects.create(
            news=news, author=author, text=f'Tекст {index}',
        )
        for index in range(10)
    ]
    for index in range(10):
        comments[index].created = now + timedelta(hours=randint(1, 24))
        comments[index].save()
    return comments


@pytest.fixture
def comments_pk_for_args(comment):
    return comment.pk


@pytest.fixture
def form_data():
    return {
        'text': 'Новый текст',
    }
