from http import HTTPStatus
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from ..models import Post

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.first_user = User.objects.create_user(username='qwerty')
        super().setUpClass()
        Post.objects.create(
            text='first test post',
            author=cls.first_user
        )

    def setUp(self):
        self.user = User.objects.create_user(username='1234567890')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'test post',
            'group': '',
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        expected_redirect = reverse(
            'posts:profile',
            kwargs={'username': self.user.username}
        )
        self.assertRedirects(response, expected_redirect)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='test post',
                author=self.user
            ).exists()
        )

    def test_post_edit(self):
        posts_count = Post.objects.count()
        post = Post.objects.first()
        url = reverse(
            'posts:post_edit',
            kwargs={'post_id': post.id}
        )
        response = self.authorized_client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        form_data = response.context['form'].initial
        form_data['text'] = 'edited post'
        # form_data = {
        #     'text': 'edited post'
        # }
        response = self.authorized_client.post(
            url,
            data=form_data,
            follow=True
        )
        expected_redirect = reverse(
            'posts:post_detail',
            kwargs={'post_id': post.id}
        )
        self.assertRedirects(response, expected_redirect)
        self.assertEqual(Post.objects.count(), posts_count)
        print(Post.objects.get(id=post.id))
        self.assertTrue(
            Post.objects.filter(
                id=post.id,
                text='edited post'
            )
        )
