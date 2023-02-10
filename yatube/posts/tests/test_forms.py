from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from posts.forms import PostForm
from posts.models import Comment, Post, User
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class PostsCreateFormTests(TestCase):
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
        cls.user = User.objects.create(username='TestUser')
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            image=test_image
        )
        cls.form = PostForm()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.comments_count = Comment.objects.count()

    def test_create_post(self):
        # тест создания поста
        post_count = Post.objects.count()
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
        form_data = {
            'text': 'Текст пробного поста 1',
            'group': 'Тестовая группа',
            'image': test_image
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # тест создания нового поста
        self.assertEqual(Post.objects.count(), post_count)
        self.assertEqual(response.status_code, 200)
        # Тест изменения текста
        post = Post.objects.get(id=self.post.pk)
        self.assertEqual(post.text, 'Тестовый текст')

    def test_create_comment(self):
        # проверяем появление комментария после отправки
        comments_count = Comment.objects.count()
        form_data = {'text': 'тестовый уксусный комментарий'}
        response = self.authorized_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertContains(response, 'тестовый уксусный комментарий')
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertRedirects(
            response, reverse('posts:post_detail', args={self.post.id}))

    def test_create_comment_only_authorized_user(self):
        # проверяем что комментарий авторизированным не добавляется
        self.guest_client = Client()
        form_data = {'text': 'тестовый второй комментарий, политый уксусом'}
        self.guest_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        new_comments_count = Comment.objects.count()
        self.assertEqual(new_comments_count, self.comments_count)
