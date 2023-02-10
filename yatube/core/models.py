from django.db import models


class CreatedModel(models.Model):
    # абстрактная модель для создания даты публикации/комментария
    created = models.DateTimeField(
        'дата создания',
        auto_now_add=True
    )

    class Meta:
        abstract = True
