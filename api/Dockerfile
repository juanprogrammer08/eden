FROM python:3.12-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de requerimientos y luego instalar dependencias
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente de la aplicación
COPY ./app ./app

# Exponer el puerto en el que correrá la API
EXPOSE 8000

# Comando para ejecutar la aplicación con uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]