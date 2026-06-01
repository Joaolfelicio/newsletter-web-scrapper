import logging

import azure.functions as func

from src.checkers.rss import RSSFeedChecker
from src.notifiers.telegram import TelegramNotifier
from src.storage.azure_tables import AzureTablesStorage

app = func.FunctionApp()

CHECKERS = [
    RSSFeedChecker("Faros Blog", "https://www.faros.ai/blog/rss.xml"),
]


@app.timer_trigger(
    schedule="0 0 * * * *",
    arg_name="timer",
    run_on_startup=False,
    use_monitor=False,
)
def check_feeds(timer: func.TimerRequest) -> None:
    storage = AzureTablesStorage()
    notifier = TelegramNotifier()

    for checker in CHECKERS:
        try:
            articles = checker.get_articles()
        except Exception:
            logging.exception("Failed to fetch articles from %s", checker.site_name)
            continue

        for article in articles:
            if storage.is_new(article):
                try:
                    notifier.send_article(article)
                    storage.mark_seen(article)
                    logging.info("Notified: %s — %s", checker.site_name, article.title)
                except Exception:
                    logging.exception("Failed to notify for %s", article.url)
