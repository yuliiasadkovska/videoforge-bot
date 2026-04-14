"""
Claude Code integration for Telegram bot (Webhook version for Railway)

Instead of launching PowerShell directly, sends webhook to PC Agent.
"""

import os
import requests
import logging

log = logging.getLogger("claude_webhook")

PC_AGENT_URL = os.getenv("PC_AGENT_URL", "").strip()
PC_AGENT_SECRET = os.getenv("PC_AGENT_SECRET", "change-this-secret-key-123").strip()

def register_claude_commands(bot, auth_func=None):
    """
    Register Claude commands that work via webhook to PC Agent.

    Returns dict with handlers for button integration.
    """

    def _send_webhook(model: str, chat_id: int) -> dict:
        """Send webhook to PC Agent to launch Claude script."""
        if not PC_AGENT_URL:
            return {"ok": False, "error": "PC_AGENT_URL not configured"}

        try:
            response = requests.post(
                f"{PC_AGENT_URL}/webhook/claude/launch",
                json={
                    "model": model,
                    "user_id": chat_id,
                    "secret": PC_AGENT_SECRET
                },
                timeout=10
            )

            if response.status_code == 200:
                return {"ok": True, "data": response.json()}
            else:
                return {"ok": False, "error": f"HTTP {response.status_code}: {response.text}"}
        except Exception as e:
            log.error(f"Webhook error: {e}")
            return {"ok": False, "error": str(e)}

    def _handle_sonnet(message):
        """Launch Claude Sonnet via webhook."""
        if auth_func and not auth_func(message):
            return

        bot.reply_to(message, "🧠 Запускаю Claude Sonnet на твоєму ПК...")

        result = _send_webhook("sonnet", message.chat.id)

        if result["ok"]:
            bot.reply_to(message, "✅ Claude Sonnet запущено!")
        else:
            bot.reply_to(message, f"❌ Помилка: {result.get('error', 'Unknown')}")

    def _handle_opus(message):
        """Launch Claude Opus via webhook."""
        if auth_func and not auth_func(message):
            return

        bot.reply_to(message, "💎 Запускаю Claude Opus на твоєму ПК...")

        result = _send_webhook("opus", message.chat.id)

        if result["ok"]:
            bot.reply_to(message, "✅ Claude Opus запущено!")
        else:
            bot.reply_to(message, f"❌ Помилка: {result.get('error', 'Unknown')}")

    def _handle_clear(message):
        """Clear Claude history (not implemented via webhook)."""
        if auth_func and not auth_func(message):
            return

        bot.reply_to(message, "ℹ️ Очищення історії доступне тільки локально")

    def _handle_quota(message):
        """Check Opus quota."""
        if auth_func and not auth_func(message):
            return

        # Check quota via direct API call (doesn't need PC)
        opus_base_url = "http://46.173.17.179:3188"
        opus_api_key = os.getenv("OPUS_API_KEY", "").strip()

        if not opus_api_key:
            bot.reply_to(message, "❌ OPUS_API_KEY не налаштований")
            return

        try:
            response = requests.get(
                f"{opus_base_url}/v1/quota",
                headers={"x-api-key": opus_api_key},
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()
                used = data.get("usage", {}).get("total_tokens", 0)
                limit = data.get("limit", {}).get("total_tokens", 0)
                remaining = limit - used

                msg = f"💰 **Opus Quota**\n\n"
                msg += f"Використано: {used:,} токенів\n"
                msg += f"Ліміт: {limit:,} токенів\n"
                msg += f"Залишилось: {remaining:,} токенів"

                bot.reply_to(message, msg, parse_mode="Markdown")
            else:
                bot.reply_to(message, f"❌ Помилка API: {response.status_code}")
        except Exception as e:
            bot.reply_to(message, f"❌ Помилка: {str(e)}")

    # Register commands
    @bot.message_handler(commands=["claude_sonnet"])
    def cmd_sonnet(message):
        _handle_sonnet(message)

    @bot.message_handler(commands=["claude_opus"])
    def cmd_opus(message):
        _handle_opus(message)

    @bot.message_handler(commands=["claude_quota"])
    def cmd_quota(message):
        _handle_quota(message)

    log.info("Claude webhook commands registered")

    # Return handlers for button integration
    return {
        "handlers": {
            "🧠 Claude Sonnet": _handle_sonnet,
            "💎 Claude Opus": _handle_opus,
            "🗑️ Очистити історію": _handle_clear,
            "💰 Токени Opus": _handle_quota,
        }
    }
