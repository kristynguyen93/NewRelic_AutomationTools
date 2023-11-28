import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

accountId = int(os.getenv("NEW_RELIC_ACCOUNT_ID"))
api_key = os.getenv("NEW_RELIC_API_KEY")
graphql_url = 'https://api.newrelic.com/graphql'

headers = {
    'Content-Type': 'application/json',
    'API-Key': api_key
}