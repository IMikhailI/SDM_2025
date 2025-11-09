# API Документация - EduNext Backend


> Полная интерактивная документация: **Swagger UI** - `/api/docs/`

---

## 🧰 Подготовка (получение токена, чтобы примеры работали)

1) **Регистрация пользователя** (один раз):
```bash
curl -i -X POST http://127.0.0.1:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"tester","password":"tester_pass"}'
```
> Если пользователь уже существует, можно сразу перейти к шагу 2.

2) **Получение JWT‑токена**:
```bash
TOKENS=$(curl -sS -X POST http://127.0.0.1:8000/api/auth/token \
  -H 'Content-Type: application/json' \
  -d '{"username":"tester","password":"tester_pass"}')
```

3) (Опционально) **Сохранить токен в переменную окружения** (для примеров ниже):
```bash
ACCESS=$(python3 -c 'import sys,json; print(json.load(sys.stdin)["access"])' <<<"$TOKENS")
```

---

## Содержание
1. [Аутентификация](#Аутентификация)
   - [POST /api/auth/register/](#post-apiauthregister)
   - [POST /api/auth/token/](#post-apiauthtoken)
   - [POST /api/auth/token/refresh/](#post-apiauthtokenrefresh)
2. [Курсы](#Курсы)
   - [GET /api/courses/](#get-apicourses)
   - [POST /api/courses/](#post-apicourses)
   - [GET /api/courses/{id}/](#get-apicoursesid)
   - [PUT /api/courses/{id}/](#put-apicoursesid)
   - [PATCH /api/courses/{id}/](#patch-apicoursesid)
   - [DELETE /api/courses/{id}/](#delete-apicoursesid)
3. [Уроки](#Уроки)
   - [GET /api/lessons/](#get-apilessons)
   - [POST /api/lessons/](#post-apilessons)
   - [GET /api/lessons/{id}/](#get-apilessonsid)
   - [PUT /api/lessons/{id}/](#put-apilessonsid)
   - [PATCH /api/lessons/{id}/](#patch-apilessonsid)
   - [DELETE /api/lessons/{id}/](#delete-apilessonsid)
4. [Прогресс урока](#Прогресс-урока)
   - [POST /api/lessons/{id}/complete/](#post-apilessonsidcomplete)
5. [AI‑вопрос по уроку](#ai-вопрос-по-уроку)
   - [POST /api/lessons/{id}/ask/](#post-apilessonsidask)


> В примерах с изменением данных (`POST/PUT/PATCH/DELETE`) предполагается, что в переменной окружения `ACCESS` лежит корректный access‑токен.

---

## Аутентификация

### POST /api/auth/register/
Создаёт нового пользователя.

**Тело запроса**
```json
{ "username": "tester", "password": "tester_pass" }
```

**Успех: 201 Created**
```json
{ "id": 1, "username": "tester" }
```

**Пример (curl)**
```bash
curl -X POST http://127.0.0.1:8000/api/auth/register/   -H "Content-Type: application/json"   -d '{"username":"tester","password":"tester_pass"}'
```

---

### POST /api/auth/token/
Возвращает пару токенов JWT.

**Тело запроса**
```json
{ "username": "tester", "password": "tester_pass" }
```

**Успех: 200 OK**
```json
{ "refresh": "<refresh-jwt>", "access": "<access-jwt>" }
```

**Пример (curl)**
```bash
curl -X POST http://127.0.0.1:8000/api/auth/token/   -H "Content-Type: application/json"   -d '{"username":"tester","password":"tester_pass"}'
```

---

### POST /api/auth/token/refresh/
Обновляет access‑токен по refresh‑токену.

**Тело запроса**
```json
{ "refresh": "<refresh-jwt>" }
```

**Успех: 200 OK**
```json
{ "access": "<new-access-jwt>" }
```

**Пример (curl)**
```bash
curl -X POST http://127.0.0.1:8000/api/auth/token/refresh/   -H "Content-Type: application/json"   -d '{"refresh":"<refresh-jwt>"}'
```

---

## Курсы

### GET /api/courses/
Список курсов.

**Успех: 200 OK**
```json
[ { "id": 1, "title": "Python Basics", "description": "..." } ]
```

**Пример (curl)**
```bash
curl -s http://127.0.0.1:8000/api/courses/
```

---

### POST /api/courses/  *(JWT)*
Создать курс.

**Тело запроса**
```json
{ "title": "Python Basics", "description": "Стартовый курс" }
```

**Успех: 201 Created**
```json
{ "id": 2, "title": "Python Basics", "description": "Стартовый курс" }
```

**Рабочий пример (curl)**
```bash
curl -X POST http://127.0.0.1:8000/api/courses/   -H "Authorization: Bearer $ACCESS"   -H "Content-Type: application/json"   -d '{"title":"Python Basics","description":"Стартовый курс"}'
```

---

### GET /api/courses/{id}/
Получить курс по `id`.

**Успех: 200 OK**
```json
{ "id": 1, "title": "Python Basics", "description": "..." }
```

**Рабочий пример (curl)**
```bash
COURSE_ID=1
curl -s http://127.0.0.1:8000/api/courses/$COURSE_ID/
```

---

### PUT /api/courses/{id}/  *(JWT)*
Полностью обновить курс.

**Тело запроса**
```json
{ "title": "New title", "description": "New description" }
```

**Рабочий пример (curl)**
```bash
COURSE_ID=1
curl -X PUT http://127.0.0.1:8000/api/courses/$COURSE_ID/   -H "Authorization: Bearer $ACCESS"   -H "Content-Type: application/json"   -d '{"title":"New title","description":"New description"}'
```

---

### PATCH /api/courses/{id}/  *(JWT)*
Частично обновить курс.

**Тело запроса (пример)**
```json
{ "description": "Обновлённое описание" }
```

**Рабочий пример (curl)**
```bash
COURSE_ID=1
curl -X PATCH http://127.0.0.1:8000/api/courses/$COURSE_ID/   -H "Authorization: Bearer $ACCESS"   -H "Content-Type: application/json"   -d '{"description":"Обновлённое описание"}'
```

---

### DELETE /api/courses/{id}/  *(JWT)*
Удалить курс.

**Успех: 204 No Content**

**Рабочий пример (curl)**
```bash
COURSE_ID=2
curl -X DELETE http://127.0.0.1:8000/api/courses/$COURSE_ID/   -H "Authorization: Bearer $ACCESS"
```

---

## Уроки

### GET /api/lessons/
Список уроков. Поддерживает фильтр `?course={course_id}`.

**Успех: 200 OK**
```json
[ { "id": 10, "course": 1, "title": "Variables", "content": "..." } ]
```

**Рабочие примеры (curl)**
```bash
curl -s http://127.0.0.1:8000/api/lessons/
curl -s "http://127.0.0.1:8000/api/lessons/?course=1"
```

---

### POST /api/lessons/  *(JWT)*
Создать урок.

**Тело запроса**
```json
{ "course": 1, "title": "Variables", "content": "Текст урока" }
```

**Успех: 201 Created**
```json
{ "id": 11, "course": 1, "title": "Variables", "content": "Текст урока" }
```

**Рабочий пример (curl)**
```bash
curl -X POST http://127.0.0.1:8000/api/lessons/   -H "Authorization: Bearer $ACCESS"   -H "Content-Type: application/json"   -d '{"course":1,"title":"Variables","content":"Текст урока"}'
```

---

### GET /api/lessons/{id}/
Получить урок по `id`.

**Рабочий пример (curl)**
```bash
LESSON_ID=1
curl -s http://127.0.0.1:8000/api/lessons/$LESSON_ID/
```

---

### PUT /api/lessons/{id}/  *(JWT)*
Полностью обновить урок.

**Тело запроса**
```json
{ "course": 1, "title": "New", "content": "..." }
```

**Рабочий пример (curl)**
```bash
LESSON_ID=1
curl -X PUT http://127.0.0.1:8000/api/lessons/$LESSON_ID/   -H "Authorization: Bearer $ACCESS"   -H "Content-Type: application/json"   -d '{"course":1,"title":"New","content":"..."}'
```

---

### PATCH /api/lessons/{id}/  *(JWT)*
Частично обновить урок.

**Тело запроса (пример)**
```json
{ "title": "Variables - updated" }
```

**Рабочий пример (curl)**
```bash
LESSON_ID=1
curl -X PATCH http://127.0.0.1:8000/api/lessons/$LESSON_ID/   -H "Authorization: Bearer $ACCESS"   -H "Content-Type: application/json"   -d '{"title":"Variables - updated"}'
```

---

### DELETE /api/lessons/{id}/  *(JWT)*
Удалить урок.

**Успех: 204 No Content**

**Рабочий пример (curl)**
```bash
LESSON_ID=11
curl -X DELETE http://127.0.0.1:8000/api/lessons/$LESSON_ID/   -H "Authorization: Bearer $ACCESS"
```

---

## Прогресс урока

### POST /api/lessons/{id}/complete/  *(JWT)*
Отмечает урок как пройденный текущим пользователем.

**Успех: 200 OK / 201 Created**
```json
{ "id": 5, "user": 1, "lesson": 1, "completed_at": "2025-10-28T20:10:31Z" }
```

**Рабочий пример (curl)**
```bash
LESSON_ID=1
curl -X POST http://127.0.0.1:8000/api/lessons/$LESSON_ID/complete/   -H "Authorization: Bearer $ACCESS"
```

---

## AI‑вопрос по уроку

### POST /api/lessons/{id}/ask/  *(JWT)*
Задаёт вопрос по контенту урока и возвращает ответ от AI‑провайдера.

**Тело запроса**
```json
{ "question": "Объясни разницу между var и let", "provider": "gigachat" }
```
- `provider` - необязательное поле: `"gigachat"` или `"google"`; если не указано, используется первый доступный из `DEFAULT_PROVIDERS`.

**Успех: 200 OK**
```json
{ "answer": "...текст ответа...", "provider": "gigachat" }
```

**Рабочий пример (curl)**
```bash
LESSON_ID=1
curl -X POST http://127.0.0.1:8000/api/lessons/$LESSON_ID/ask/   -H "Authorization: Bearer $ACCESS"   -H "Content-Type: application/json"   -d '{"question":"В чём разница var/let?","provider":"google"}'
```

---
