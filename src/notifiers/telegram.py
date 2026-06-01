import os

import requests

from src.models import Article

_API_BASE = "https://api.telegram.org"


class TelegramNotifier:
    def __init__(self) -> None:
        self._token = os.environ["TELEGRAM_BOT_TOKEN"]
        self._chat_id = os.environ["TELEGRAM_CHAT_ID"]

    def send_article(self, article: Article) -> None:
        response = requests.post(
            f"{_API_BASE}/bot{self._token}/sendMessage",
            json={
                "chat_id": self._chat_id,
                "text": article.url,
            },
            timeout=10,
        )
        response.raise_for_status()
