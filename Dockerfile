FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements_railway.txt .
RUN pip install --no-cache-dir -r requirements_railway.txt

# Copy bot files
COPY tg_bot.py .
COPY tunnel_utils.py .
# Copy webhook version of Claude module (sends commands to PC Agent)
COPY claude_module_webhook.py claude_module.py
# Note: .env is not needed on Railway - environment variables are injected via Railway Variables

# Run bot
CMD ["python", "tg_bot.py"]
