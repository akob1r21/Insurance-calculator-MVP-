# Dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
  && apt-get install -y --no-install-recommends gcc libpq-dev postgresql-client \
  && rm -rf /var/lib/apt/lists/*

# copy requirements and install
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip \
  && pip install --no-cache-dir -r /app/requirements.txt

# copy project
COPY . /app/

RUN adduser --disabled-password --gecos "" appuser \
  && chown -R appuser:appuser /app

USER appuser

RUN chmod +x /app/entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "bima.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
