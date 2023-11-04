import pytest

from django.urls import reverse


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('comments_pk_for_args')),
    )
)
def test_pages_contains_form(author_client, name, args):
    url = reverse(name, args=(args,))
    response = author_client.get(url)
    assert 'form' in response.context
