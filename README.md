# EduNext Backend

Django + DRF сервис для учебной платформы с курсами и уроками, трекингом прогресса пользователя и AI‑помощником (GigaChat / Google). Проект аккуратно документирован, снабжён готовой фикстурой данных и автогенерируемой Swagger‑документацией.

---

## 🧱 Стек
- **Python**, **Django 5**, **Django REST Framework**
- **PostgreSQL**
- **drf-spectacular** (OpenAPI/Swagger)

---

# Основное задание
## 📁 Модели бд
- `Course(title, description)` - курс.
- `Lesson(course, title, content)` - урок, привязан к курсу.
- `UserProgress(user, lesson, completed_at)` - факт прохождения урока пользователем.

> Модели и сериализаторы находятся в `models.py` и `serializers.py` в корне приложения.

---

## 🚀 Быстрый старт

### 1) Клонирование и окружение
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Создайте `.env` в корне проекта (или используйте уже добавленный) со своими значениями:

```dotenv
DEBUG=True
SECRET_KEY=change-me
ALLOWED_HOSTS=*

DB_NAME=edunext
DB_USER=edunext
DB_PASSWORD=edunext
DB_HOST=127.0.0.1
DB_PORT=5432

# AI (опционально для /api/lessons/{id}/ask)
DEFAULT_PROVIDERS=gigachat,google

GOOGLE_API_KEY=...
GOOGLE_MODEL=gemini-2.5-flash

# Для GigaChat (если используете его)
SBER_BASIC_AUTH=...        # base64(client_id:client_secret) или аналогичный токен в вашей реализации
SBER_AUTH_URL=...
SBER_API_URL=...
```

### 2) Поднять PostgreSQL
Локально через Docker:
```bash
docker run --name edunext-db -e POSTGRES_USER=edunext -e POSTGRES_PASSWORD=edunext -e POSTGRES_DB=edunext -p 5432:5432 -d postgres:16
```
Или вручную (пример для psql):
```sql
CREATE USER edunext WITH PASSWORD 'edunext';
CREATE DATABASE edunext OWNER edunext;
GRANT ALL PRIVILEGES ON DATABASE edunext TO edunext;
```

### 3) Миграции и суперпользователь
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 4) Загрузка стартовых данных (фикстура)
Лежит в `courses/fixtures/seed_courses_lessons.json` 
```bash
python manage.py loaddata courses/fixtures/seed_courses_lessons.json
```

### 5) Запуск
```bash
python manage.py runserver
```
- Swagger UI: `http://127.0.0.1:8000/api/docs/`
- Админка: `http://127.0.0.1:8000/admin/`

---

## 🔐 Аутентификация
Используется **JWT** (access/refresh). Последовательность:
1. **Регистрация**: `POST /api/auth/register`  
   Тело:
   ```json
   { "username": "tester", "password": "tester_pass" }
   ```
2. **Получить токены**: `POST /api/auth/token`  
   Тело:
   ```json
   { "username": "tester", "password": "tester_pass" }
   ```
   Ответ содержит `access` и `refresh`.
3. **Обновить access**: `POST /api/auth/token/refresh`  
   Тело:
   ```json
   { "refresh": "<refresh-token>" }
   ```

Передавайте `Authorization: Bearer <access>` для защищённых методов.

---

## 📚 Документация по API (кратко)


> Полная спецификация: [API.md](./API.md).

> Интерактивная документация доступна в Swagger UI: `/api/docs`.
### Курсы
- `GET /api/courses` - список курсов.
- `POST /api/courses` - создать курс. *(JWT)*
- `GET /api/courses/{id}` - получить курс.
- `PUT/PATCH /api/courses/{id}` - обновить курс. *(JWT)*
- `DELETE /api/courses/{id}` - удалить курс. *(JWT)*

**Пример**:
```bash
curl -s "http://127.0.0.1:8000/api/courses"
```

### Уроки
- `GET /api/lessons` - список уроков, поддерживает фильтр по курсу: `?course={course_id}`.
- `POST /api/lessons` - создать урок. *(JWT)*
- `GET /api/lessons/{id}` - получить урок.
- `PUT/PATCH /api/lessons/{id}` - обновить урок. *(JWT)*
- `DELETE /api/lessons/{id}` - удалить урок. *(JWT)*

**Пример**:
```bash
curl -s "http://127.0.0.1:8000/api/lessons?course=1"
```

### Прогресс прохождения
- `POST /api/lessons/{id}/complete` - отметить урок как пройденный текущим пользователем. *(JWT)*  
  **Ответ**: запись `UserProgress` или статус «уже пройдено».

### Вопрос к уроку (AI)
- `POST /api/lessons/{id}/ask` - задать вопрос по содержимому урока и получить ответ от выбранного AI‑провайдера. *(JWT)*  
  **Тело запроса**:
  ```json
  { "question": "Объясни разницу между var и let", "provider": "gigachat" }
  ```
  `provider` - необязательное поле (`gigachat` или `google`). Если не указать, используется значение по умолчанию из `DEFAULT_PROVIDERS` (первый доступный).  
  **Ответ**:
  ```json
  { "answer": "...текст ответа...", "provider": "gigachat" }
  ```

---

# Использование ИИ

> Описание как использовал ИИ: [AI.md](./AI.md).
