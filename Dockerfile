
FROM python:3.12-slim

# Directorio principal del contenedor
WORKDIR /usr/app/src

# Copiar dependencias
COPY requirements.txt .

# Instalar dependencias dentro de Docker
RUN pip install --no-cache-dir -r requirements.txt

# Copiar archivos del proyecto
COPY notebooks/ ./notebooks/
#COPY utils/ ./utils/

# Comando predeterminado
CMD ["python", "--version"]
