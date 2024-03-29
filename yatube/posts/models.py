from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(
        max_length=50,
        unique=True
    )
    description = models.TextField()

    def __str__(self) -> str:
        return self.title[:25]

    class Meta:
        verbose_name_plural = 'Группы'


class Post(models.Model):
    text = models.TextField(
        verbose_name='текст',
        help_text='текст публикации')
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='дата публикации')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='автор поста',
        help_text='Выберите автора'
    )
    group = models.ForeignKey(
        'Group',
        on_delete=models.SET_NULL,
        related_name='posts',
        blank=True,
        null=True,
        verbose_name='группа',
        help_text='выберите группу'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        verbose_name_plural = 'Посты'
        ordering = ['-pub_date']

    def __str__(self) -> str:
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    text = models.TextField(
        verbose_name='Оставьте Ваш комментарий',
        help_text='текст комментария'
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='дата комментария'
    )

    class Meta:
        verbose_name_plural = 'Комментарии'
        ordering = ['-created']


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
    )

    class Meta:
        verbose_name_plural = 'Подписки'
        constraints = [models.UniqueConstraint(
            fields=['user', 'author'], name='unique_follow')]
