# Gunakan image dasar dengan Python terinstal
FROM python:3.8-slim

# Set working directory
WORKDIR /app

# Salin file requirements.txt ke dalam image
COPY requirements.txt .

# Instal semua dependensi yang tercantum di requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Salin semua file aplikasi ke dalam image
COPY . .

# Salin file kredensial ke dalam image
COPY ML-API2.json /app/

# Salin file model ke dalam image
COPY Recycleme-Model.h5 /app/

# Setel variabel lingkungan untuk file kredensial
ENV GOOGLE_APPLICATION_CREDENTIALS="/app/ML-API2.json"

# Tentukan port yang digunakan aplikasi (opsional)
EXPOSE 8080

# Jalankan aplikasi
CMD ["python", "main.py"]
