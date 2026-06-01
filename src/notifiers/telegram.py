import os

import requests

from src.models import Article

_API_BASE = "https://api.telegram.org"


def _escape(text: str) -> str:
    for ch in ("&", "<", ">"):
        text = text.replace(ch, {"&": "&amp;", "<": "&lt;", ">": "&gt;"}[ch])
    return text


class TelegramNotifier:
    def __init__(self) -> None:
        self._token = os.environ["TELEGRAM_BOT_TOKEN"]
        self._chat_id = os.environ["TELEGRAM_CHAT_ID"]

    def send_article(self, article: Article) -> None:
        description = article.description[:300]
        text = (
            f"<b>New article — {_escape(article.site_name)}</b>\n\n"
            f'<a href="{article.url}">{_escape(article.title)}</a>\n'
            f"<i>{_escape(description)}</i>"
        )
        response = requests.post(
            f"{_API_BASE}/bot{self._token}/sendMessage",
            json={
                "chat_id": self._chat_id,
                "text": text,
                "parse_mode": "HTML",
                "link_preview_options": {"is_disabled": False},
            },
            timeout=10,
        )
        response.raise_for_status()
