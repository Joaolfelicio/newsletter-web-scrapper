# newsletter-web-scrapper

Azure Function that monitors blog RSS feeds and sends Telegram notifications when new articles are published. Runs hourly. Idempotent — uses Azure Storage Tables to track seen articles across runs.

## Adding a new site

In `function_app.py`, add an entry to `CHECKERS`:

```python
CHECKERS = [
    RSSFeedChecker("Faros Blog", "https://www.faros.ai/blog/rss.xml"),
    RSSFeedChecker("My Site", "https://example.com/rss.xml"),
]
```

For sites without RSS, subclass `BaseFeedChecker` in `src/checkers/` and implement `get_articles()`.

## Setup

### 1. Telegram bot

1. Get the **bot token**: message `@BotFather` → `/mybots` → select the bot → API Token
2. Start a conversation with the bot (or add it to a group)
3. Get your **chat ID** (numeric):
   - Send a message to the bot first
   - Visit `https://api.telegram.org/bot<TOKEN>/getUpdates` in a browser
   - Look for `"chat":{"id":<number>}` — that number is `TELEGRAM_CHAT_ID`

### 2. GitHub secrets

Go to your repo → **Settings → Secrets and variables → Actions → Secrets**.

| Name | Value |
|------|-------|
| `AZURE_CREDENTIALS` | Output of `az ad sp create-for-rbac --name newsletter-deploy --role contributor --scopes /subscriptions/<sub-id>/resourceGroups/rg-newsletter-scrapper --sdk-auth` |
| `TELEGRAM_BOT_TOKEN` | From BotFather |
| `TELEGRAM_CHAT_ID` | Your chat/group ID |

All Azure resource names and location are hardcoded in `.github/workflows/deploy.yml`. Azure resources are provisioned automatically on first deploy — no manual `az` commands needed.

### 3. Deploy

Push to `main` — GitHub Actions handles the rest.

## Local development

```bash
pip install -r requirements.txt
# Fill in local.settings.json with real values
func start
```

To trigger manually: in Azure portal → your function → **Code + Test → Test/Run**.
