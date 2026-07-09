FROM python:3.11-slim

WORKDIR /app

# Install FFmpeg & Node.js for yt-dlp
RUN apt-get update && \
    apt-get install -y ffmpeg curl && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run the API
CMD ["uvicorn", "YUKIYTAPI.main:app", "--host", "0.0.0.0", "--port", "8000"]
