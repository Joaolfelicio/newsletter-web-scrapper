import hashlib
import os
import re

from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from azure.data.tables import TableServiceClient
from azure.identity import DefaultAzureCredential

from src.models import Article

_TABLE_NAME = "SeenArticles"


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "-", text.lower())[:50].strip("-")


def _row_key(guid: str) -> str:
    return hashlib.sha256(guid.encode()).hexdigest()[:32]


class AzureTablesStorage:
    def __init__(self) -> None:
        endpoint = os.environ["AZURE_TABLES_ENDPOINT"]
        credential = DefaultAzureCredential()
        service = TableServiceClient(endpoint=endpoint, credential=credential)
        try:
            service.create_table(_TABLE_NAME)
        except ResourceExistsError:
            pass
        self._client = service.get_table_client(_TABLE_NAME)

    def is_new(self, article: Article) -> bool:
        try:
            self._client.get_entity(
                partition_key=_slug(article.site_name),
                row_key=_row_key(article.guid),
            )
            return False
        except ResourceNotFoundError:
            return True

    def mark_seen(self, article: Article) -> None:
        self._client.upsert_entity(
            {
                "PartitionKey": _slug(article.site_name),
                "RowKey": _row_key(article.guid),
                "title": article.title,
                "url": article.url,
            }
        )
