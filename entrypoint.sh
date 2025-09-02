#!/bin/sh
set -e

# Wait for postgres (respect POSTGRES_HOST)
if [ -n "${POSTGRES_HOST}" ]; then
  echo "Waiting for postgres at ${POSTGRES_HOST}:${POSTGRES_PORT:-5432}..."
  until pg_isready -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT:-5432}" -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" >/dev/null 2>&1; do
    echo "Postgres unavailable - sleeping"
    sleep 1
  done
fi

echo "Apply migrations..."
python manage.py migrate --noinput

echo "Collect static..."
python manage.py collectstatic --noinput || true

# create superuser if env provided (non-interactive)
if [ -n "${DJANGO_SUPERUSER_USERNAME}" ] && [ -n "${DJANGO_SUPERUSER_EMAIL}" ] && [ -n "${DJANGO_SUPERUSER_PASSWORD}" ]; then
  echo "Ensuring superuser ${DJANGO_SUPERUSER_USERNAME}..."
  python manage.py shell -c "from django.contrib.auth import get_user_model; User=get_user_model(); \
  username='${DJANGO_SUPERUSER_USERNAME}'; email='${DJANGO_SUPERUSER_EMAIL}'; \
  if not User.objects.filter(username=username).exists(): \
    User.objects.create_superuser(username=username, email=email, password='${DJANGO_SUPERUSER_PASSWORD}'); \
  print('superuser ensured')"
fi

exec "$@"
