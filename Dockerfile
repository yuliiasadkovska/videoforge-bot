FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements_railway.txt .
RUN pip install --no-cache-dir -r requirements_railway.txt

# Copy bot files (only bot, not Claude module - it won't work on Railway anyway)
COPY tg_bot.py .
COPY tunnel_utils.py .
COPY ai_team.py .
# Note: .env is not needed on Railway - environment variables are injected via Railway Variables

# Run bot
CMD ["python", "tg_bot.py"]
