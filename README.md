# EduNext Backend

<p align="center">
  Backend учебной платформы с курсами, уроками, прогрессом и AI-помощником.
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3-3776AB?logo=python&logoColor=white">
  <img alt="Django" src="https://img.shields.io/badge/Django-5-092E20?logo=django&logoColor=white">
  <img alt="DRF" src="https://img.shields.io/badge/API-Django%20REST%20Framework-A30000">
  <img alt="PostgreSQL" src="https://img.shields.io/badge/Database-PostgreSQL-4169E1?logo=postgresql&logoColor=white">
</p>

EduNext предоставляет REST API для учебных курсов. Пользователи просматривают курсы и уроки, отмечают прохождение и могут задавать вопросы по материалу через подключённого AI-провайдера.

## Возможности

- курсы, уроки и прогресс пользователя;
- регистрация и JWT-аутентификация;
- API для управления учебным содержимым;
- генерация заданий;
- Swagger UI через **/api/docs/**;
- PostgreSQL как основная база данных.

## Стек

Python · Django 5 · Django REST Framework · PostgreSQL · drf-spectacular

## Локальный запуск

~~~bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
~~~

Затем создайте PostgreSQL-базу и пользователя для приложения, укажите подключение и секреты в локальной конфигурации окружения, примените миграции и запустите сервер:

~~~bash
python manage.py migrate
python manage.py runserver
~~~

Swagger UI: **http://127.0.0.1:8000/api/docs/**. Для генерации ответов AI задайте ключи выбранного провайдера в окружении. Не помещайте действующие ключи в Git.

## Безопасность перед публичным использованием

В репозитории отслеживается файл **.env**. Проверьте его локально, не копируя значения в README или сообщения. Если там есть реальные пароли, ключи или токены, отзовите их и замените; затем исключите файл из Git и при необходимости очистите его из истории. README намеренно не содержит значений из этого файла.