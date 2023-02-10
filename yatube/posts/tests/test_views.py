import math
import shutil
import tempfile


from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse


from ..models import Follow, Group, Post
from ..forms import PostForm

User = get_user_model()


# временная папка для сохранения картинок при тестировании
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        test_image = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.user = User.objects.create_user(username='bilbo')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='slug_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
            image=test_image
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Метод shutil.rmtree удаляет временную папку после тестирования
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон"""
        templates_page_names = {
            reverse('posts:index'): 'posts/index.html',
            (
                reverse('posts:group_list', kwargs={'slug': 'slug_slug'})
            ): 'posts/group_list.html',
            (
                reverse('posts:profile', kwargs={
                    'username': self.user.username
                })
            ): 'posts/profile.html',
            (
                reverse('posts:post_detail', kwargs={'post_id': self.post.pk})
            ): 'posts/post_detail.html',
            (
                reverse('posts:post_edit', kwargs={'post_id': self.post.pk})
            ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_page_names.items():
            with self.subTest(template=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_cache(self):
        """страница index кэшируется"""
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        posts = response.content
        Post.objects.create(
            text='запись для проверки кэша',
            author=self.user,
        )
        old_response = self.authorized_client.get(reverse('posts:index'))
        old_posts = old_response.content
        self.assertEqual(old_posts, posts)
        cache.clear()
        new_response = self.authorized_client.get(reverse('posts:index'))
        new_posts = new_response.content
        self.assertNotEqual(old_posts, new_posts)

    def check_context(self, context):
        self.assertEqual(context.pk, PostViewsTests.post.pk)
        self.assertEqual(context.text, PostViewsTests.post.text)
        self.assertEqual(context.author, PostViewsTests.post.author)
        self.assertEqual(context.image, PostViewsTests.post.image)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом"""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        self.check_context(first_object)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом"""
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': 'slug_slug'}))
        first_object = response.context['page_obj'][0]
        self.check_context(first_object)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом"""
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': 'bilbo'}))
        first_object = response.context['page_obj'][0]
        self.check_context(first_object)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом"""
        response = self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.pk}))
        first_object = response.context['post']
        self.check_context(first_object)

    def test_create_post_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом"""
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], PostForm)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='bilbo')
        cls.group_one = Group.objects.create(
            title='Тестовая группа',
            slug='slug_slug',
            description='Тестовое описание',
        )
        cls.NUMBER_POSTS: int = 20
        cls.post = [
            Post.objects.bulk_create(
                [Post(
                    author=cls.user,
                    text=f'Тестовый пост{number_of_posts}',
                    group=cls.group_one,)]) for number_of_posts in range(
                        cls.NUMBER_POSTS)
        ]

    def setUp(self):
        self.guest_client = Client()

    def test_first_page_index_gl_profile_contains_ten_records(self):
        """Проверка паджинатора первая страница"""
        number = self.NUMBER_POSTS if self.NUMBER_POSTS <= (
            settings.N_POSTS - 1) else settings.N_POSTS
        templates_page_names = [
            reverse('posts:index'),
            (
                reverse(
                    'posts:group_list', kwargs={'slug': self.group_one.slug})
            ),
            (
                reverse(
                    'posts:profile', kwargs={'username': self.user.username})
            ),
        ]
        for reverse_name in templates_page_names:
            with self.subTest(template=reverse_name):
                response = self.client.get(reverse_name)
                self.assertEqual(len(
                    response.context['page_obj']), number)

    def test_last_page_index_gl_profile_contains_ten_records(self):
        """Проверка паджинатора последняя страница"""
        pages = math.ceil(self.NUMBER_POSTS / settings.NUMBER_OF_RECORDS)
        number = self.NUMBER_POSTS if self.NUMBER_POSTS <= (
            settings.N_POSTS - 1) else ((
                (self.NUMBER_POSTS) - (int(
                    (self.NUMBER_POSTS) / settings.N_POSTS) * (
                    settings.N_POSTS))) if self.NUMBER_POSTS != (
                pages * settings.N_POSTS) else (
                    settings.N_POSTS))
        templates_page_names = [
            reverse('posts:index') + f'?page={pages}',
            reverse(
                'posts:group_list', kwargs={'slug': self.group_one.slug})
            + f'?page={pages}',
            reverse(
                'posts:profile', kwargs={'username': self.user.username})
            + f'?page={pages}',
        ]
        for reverse_name in templates_page_names:
            with self.subTest(template=reverse_name):
                response = self.client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']), number)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='bilbo')
        cls.group1 = Group.objects.create(
            title='Тестовая группа',
            slug='slug_slug',
            description='Тестовое описание',
        )
        objs = [
            Post(
                author=cls.user,
                text=n,
                group=cls.group1
            )
            for n in range(settings.N_TESTPOST)
        ]
        cls.post = Post.objects.bulk_create(objs)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_ten_records(self):
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), settings.N_POSTS)

    def test_second_page_contains_three_records(self):
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_first_page_group_list_contains_ten_records(self):
        response = self.client.get(reverse(
            'posts:group_list', kwargs={'slug': 'slug_slug'}))
        self.assertEqual(len(response.context['page_obj']), settings.N_POSTS)

    def test_first_page_profile_contains_ten_records(self):
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': 'bilbo'}))
        self.assertEqual(len(response.context['page_obj']), settings.N_POSTS)


class FollowViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='den_user')
        cls.author = User.objects.create_user(username='den_author')
        cls.unfollower = User.objects.create_user(username='unfollower_user')
        cls.new_post = Post.objects.create(
            text='запись для проверки подписки',
            author=cls.author,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.author)
        self.authorized_client_unfollower = Client()
        self.authorized_client_unfollower.force_login(self.unfollower)

    def test_profile_follow_correct(self):
        "Проверка подписки и отписки на других пользователей"
        cache.clear()
        self.authorized_client.get(reverse(
            'posts:profile_follow', kwargs={'username': self.author}))
        self.assertTrue(Follow.objects.filter(
            user=self.user, author=self.author).exists())
        self.authorized_client.get(reverse(
            'posts:profile_unfollow', kwargs={'username': self.author}))
        self.assertFalse(Follow.objects.filter(
            user=self.user, author=self.author).exists())

    def test_new_post_show_followers(self):
        """Проверка появления поста у подписчика и отсутствия у неподписчика"""
        Follow.objects.create(
            author=self.author,
            user=self.user
        )
        # проверяем появление поста у подписчика
        response = self.authorized_client.get(
            reverse('posts:follow_index'))
        context = response.context.get('page_obj').object_list
        self.assertIn(self.new_post, context)
        # проверяем отсутствие поста у неподписчика
        response = self.authorized_client_unfollower.get(
            reverse('posts:follow_index'))
        context_unfollower = response.context.get('page_obj').object_list
        self.assertNotIn(self.new_post, context_unfollower)
