from abc import ABC, abstractmethod

from src.models import Article


class BaseFeedChecker(ABC):
    site_name: str

    @abstractmethod
    def get_articles(self) -> list[Article]: ...
