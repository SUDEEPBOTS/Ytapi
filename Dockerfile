FROM python:3.11-slim

WORKDIR /app

# Install FFmpeg, Node.js, git (needed to clone bgutil provider)
RUN apt-get update && \
    apt-get install -y ffmpeg curl git && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean

# ── Setup bgutil PO token provider server ──────────────────────────────
RUN git clone --depth 1 https://github.com/Brainicism/bgutil-ytdlp-pot-provider.git /opt/bgutil-provider
WORKDIR /opt/bgutil-provider/server
RUN npm install && npx tsc

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Make start script executable
RUN chmod +x /app/start.sh

# Run both bgutil server + API
CMD ["/app/start.sh"]
