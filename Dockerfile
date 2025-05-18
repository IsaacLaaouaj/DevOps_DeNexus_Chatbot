# Imagen base
FROM python:3.10

# Evitar prompts de interacción
ENV DEBIAN_FRONTEND=noninteractive

# Crear directorio de la app
WORKDIR /app

# Copiar dependencias y código
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Cargar variables de entorno
ENV PYTHONUNBUFFERED=1

# Comando por defecto: ejecutar streamlit
CMD ["streamlit", "run", "botInterface.py", "--server.port=8501", "--server.address=0.0.0.0"]
