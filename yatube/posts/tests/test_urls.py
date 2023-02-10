from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from ..models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='leo')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Classics',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текстовый текст',
        )
        cls.expected_templates_authorized = {
            '/': 'posts/index.html',
            '/group/Classics/': 'posts/group_list.html',
            '/profile/leo/': 'posts/profile.html',
            f'/posts/{cls.post.pk}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{cls.post.pk}/edit/': 'posts/create_post.html',
        }
        cls.expected_redirect = {
            '/create/',
            f'/posts/{cls.post.pk}/edit/',
        }
        cls.expected_templates = {
            '/': 'posts/index.html',
            '/group/Classics/': 'posts/group_list.html',
            '/profile/leo/': 'posts/profile.html',
            f'/posts/{cls.post.pk}/': 'posts/post_detail.html',
        }
        cls.expected_response = {
            '/',
            '/group/Classics/',
            '/profile/leo/',
            f'/posts/{cls.post.pk}/',
            '/create/',
            f'/posts/{cls.post.pk}/edit/'
        }

    def setUp(self):
        self.guest_client = Client()

    def test_templates(self):
        # Тестируем templates неавторизованного пользователя
        for address, template in self.expected_templates.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def setUp(self):
        self.guest_client = Client()

    def test_templates(self):
        # Тестируем редирект неавторизованного пользователя
        for address in self.expected_redirect.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address, follow=True)
                self.assertRedirects(response, '/auth/login/')

    def setUp(self):
        self.guest_client = Client()
        self.user = StaticURLTests.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_templates(self):
        # Тестируем templates авторизованного пользователя
        for address, template in self.expected_templates_authorized.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_response(self):
        # Тестируем response
        for address in self.expected_response:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, 200)

    def test_response_404(self):
        response = self.authorized_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)
