import pytest

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
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        text='Текст заметки',
        author=author,
    )
    return comment


@pytest.fixture
def comments_pk_for_args(comment):
    return comment.pk


@pytest.fixture
def form_data():
    return {
        'text': 'Новый текст',
    }
