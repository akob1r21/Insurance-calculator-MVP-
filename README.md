# Страховой калькулятор (MVP)

## Описание
MVP backend-сервиса “Страховой калькулятор” на Django REST + PostgreSQL + JWT.

### Функционал
- Аутентификация:
  - POST /auth/register — регистрация
  - POST /auth/login — вход, JWT
- Расчёты:
  - POST /quotes — расчёт стоимости полиса
  - GET /quotes/{id} — просмотр расчёта
- Заявки:
  - POST /applications — создание заявки
  - GET /applications/{id} — просмотр для авторизованного пользователя
- Валидация данных и единый формат ошибок
- Миграции БД и ключевые индексы
- Документация Swagger/OpenAPI
- Docker: `docker-compose up` запускает API и PostgreSQL


### Базовый тариф (`base_price`)
- `basic` → `1000.00`
- `silver` → `1200.00`
- `gold` → `1500.00`

### Коэффициент по возрасту (`age_coef`)
- `age < 25` → `1.30` (на +30%)
- `age >= 60` → `1.20` (на +20%)
- иначе → `1.00`

### Коэффициент по стажу вождения (`exp_coef`)
- `exp < 2` → `1.40` (на +40%)
- `2 <= exp <= 5` → `1.20` (на +20%)
- `exp > 5` → `1.00`

### Коэффициент типа автомобиля (`car_coef`)
- `small` → `1.00`
- `sedan` → `1.10`
- `suv` → `1.20`

> Пример: `silver` (1200) + возраст 22 (1.30) + стаж 1 (1.40) + `suv` (1.20):  
> `1200 × 1.30 × 1.40 × 1.20 = 2620.80`

### Конфигурация `.env`
Создайте файл `.env` в корне проекта:

```ini
SECRET_KEY=super-secret-key

POSTGRES_DB=bima_db
POSTGRES_USER=bima_user
POSTGRES_PASSWORD=strongpassword
POSTGRES_HOST=db
POSTGRES_PORT=5432

SIMPLE_JWT_ACCESS_TOKEN_LIFETIME_MINUTES=60
SIMPLE_JWT_REFRESH_TOKEN_LIFETIME_DAYS=7


### Запуск через Docker
```bash
docker compose build --no-cache
docker compose up -d
