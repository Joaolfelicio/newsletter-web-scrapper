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

1. Open Telegram and message `@BotFather`
2. Send `/newbot` and follow the prompts — note the **bot token**
3. Start a conversation with your new bot (or add it to a group)
4. Get your **chat ID**:
   - Visit `https://api.telegram.org/bot<TOKEN>/getUpdates` in a browser
   - Send a message to the bot first, then refresh — look for `"chat":{"id":...}`

### 2. Azure resources (one-time)

```bash
# Variables
RG=rg-newsletter
LOCATION=westeurope
SA=newsletterstorage       # must be globally unique, lowercase, 3-24 chars
FUNCAPP=newsletter-func    # must be globally unique

# Resource group
az group create --name $RG --location $LOCATION

# Storage account
az storage account create --name $SA --resource-group $RG --location $LOCATION --sku Standard_LRS

# Function app (Python 3.13, Consumption plan)
az functionapp create \
  --name $FUNCAPP \
  --resource-group $RG \
  --storage-account $SA \
  --consumption-plan-location $LOCATION \
  --runtime python \
  --runtime-version 3.13 \
  --functions-version 4 \
  --assign-identity

# Get the managed identity principal ID
PRINCIPAL_ID=$(az functionapp identity show --name $FUNCAPP --resource-group $RG --query principalId -o tsv)
SA_ID=$(az storage account show --name $SA --resource-group $RG --query id -o tsv)

# Grant the function app permission to read/write Storage Tables
az role assignment create \
  --assignee $PRINCIPAL_ID \
  --role "Storage Table Data Contributor" \
  --scope $SA_ID
```

### 3. GitHub secrets and variables

Go to your repo → **Settings → Secrets and variables → Actions**.

**Secrets:**
| Name | Value |
|------|-------|
| `AZURE_CREDENTIALS` | Output of `az ad sp create-for-rbac --name newsletter-deploy --role contributor --scopes /subscriptions/<sub-id>/resourceGroups/<rg> --sdk-auth` |
| `AZURE_FUNCTIONAPP_NAME` | Your function app name |
| `AZURE_RESOURCE_GROUP` | Your resource group name |
| `TELEGRAM_BOT_TOKEN` | From BotFather |
| `TELEGRAM_CHAT_ID` | Your chat/group ID |

**Variables:**
| Name | Value |
|------|-------|
| `AZURE_STORAGE_ACCOUNT_NAME` | Your storage account name |

### 4. Deploy

Push to `main` — GitHub Actions handles the rest.

## Local development

```bash
pip install -r requirements.txt
# Fill in local.settings.json with real values
func start
```

To trigger manually: in Azure portal → your function → **Code + Test → Test/Run**.
