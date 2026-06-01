from dataclasses import dataclass


@dataclass
class Article:
    guid: str
    title: str
    url: str
    description: str
    site_name: str
