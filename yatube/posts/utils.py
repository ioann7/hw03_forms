from typing import TYPE_CHECKING
from django.core.paginator import Paginator
from django.conf import settings

if TYPE_CHECKING:
    from django.http.request import HttpRequest
    from django.db.models.query import QuerySet


def get_posts_page_obj(request: "HttpRequest",
                       posts: "QuerySet") -> "QuerySet":
    """Return posts page object."""
    paginator = Paginator(posts, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
