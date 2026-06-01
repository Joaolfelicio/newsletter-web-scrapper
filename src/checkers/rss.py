import html
import re
import xml.etree.ElementTree as ET

import requests

from src.checkers.base import BaseFeedChecker
from src.models import Article

_NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "media": "http://search.yahoo.com/mrss/",
}


def _text(element: ET.Element | None) -> str:
    if element is None:
        return ""
    return (element.text or "").strip()


def _strip_html(raw: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", raw)).strip()


class RSSFeedChecker(BaseFeedChecker):
    def __init__(self, site_name: str, feed_url: str) -> None:
        self.site_name = site_name
        self._feed_url = feed_url

    def get_articles(self) -> list[Article]:
        response = requests.get(self._feed_url, timeout=15)
        response.raise_for_status()

        root = ET.fromstring(response.content)
        channel = root.find("channel")
        if channel is None:
            return []

        articles = []
        for item in channel.findall("item"):
            guid = _text(item.find("guid")) or _text(item.find("link"))
            url = _text(item.find("link"))
            title = _strip_html(_text(item.find("title")))
            description = _strip_html(_text(item.find("description")))

            if not guid or not url:
                continue

            articles.append(
                Article(
                    guid=guid,
                    title=title,
                    url=url,
                    description=description,
                    site_name=self.site_name,
                )
            )

        return articles
