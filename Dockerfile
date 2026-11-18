
FROM python:3-slim

# Directorio de trabajo
WORKDIR /usr/app/src

# Copiar archivo de dependencias
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar carpetas del proyecto
COPY notebooks/ ./notebooks/
COPY utils/ ./utils/

# Exponer puerto para futura aplicación web
EXPOSE 8000

# Ejecutar el script principal
CMD ["python3", "-u", "notebooks/main.py"]
