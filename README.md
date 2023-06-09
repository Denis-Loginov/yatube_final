# yatube_final

## Описание:
Проект «Yatube» является web приложением с возможностью публикации записей с фото и комментариев к ним авторизованными пользователями.

имеет функционал пагинации и кэширования постов, а также приложение для тестирования работы проекта

Безопасность доступа реализована через аутентификацию на сонове JWT-токенов.

Незарегестрированные (не прошедшие аутентификациию) пользователи имеет права доступа только на чтение.

Аутентифицированным пользователям разрешено изменение и удаление своего контента; в остальных случаях доступ предоставляется только для чтения.


## Установка. Разворачивание проекта на локальной машине:

Клонировать репозиторий и перейти в него в командной строке:
```
git clone https://github.com/yandex-praktikum/kittygram.git
cd kittygram
```

Cоздать и активировать виртуальное окружение командами:
```
python3 -m venv env
```
для Mac:
```
source env/bin/activate 
```
для Windows 
```
source env/Scripts/activate
```

Установить зависимости из файла requirements.txt:
```
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```

Выполнить миграции:
```
python3 manage.py migrate
```

Запустить проект:
```
python3 manage.py runserver
```
