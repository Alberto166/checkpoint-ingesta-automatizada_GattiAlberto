# Usamos una imagen oficial y liviana de Python 3.11
FROM python:3.11-slim

# Evitamos que Python genere archivos .pyc y forzamos que los logs salgan directo en consola
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalamos dependencias del sistema necesarias para compilar librerías de IA y usar Git
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Establecemos el directorio de trabajo dentro del contenedor
WORKDIR /workspaces/ai-automation-project

# Copiamos e instalamos las dependencias del proyecto
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
