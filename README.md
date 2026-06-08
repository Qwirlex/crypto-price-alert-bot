# Crypto Price Alert Bot

A small Telegram bot that watches crypto prices and messages you when one of your alerts triggers. Set the coins and the rules in a config file, run it, and it pings your Telegram.

Built with Python. Uses the free CoinGecko API, so no exchange account or API key is needed for prices.

## What it does

- Tracks any coin listed on CoinGecko
- Three alert types:
  - `above`: price goes above a value
  - `below`: price drops below a value
  - `percent_change_24h`: the 24h move is bigger than a percent you set
- Sends alerts to your Telegram (direct message, group, or channel)
- Does not spam: each alert fires once, then re-arms after the condition clears

## Setup

1. Create a bot with [@BotFather](https://t.me/BotFather) and copy the token.
2. Get your chat id (message [@userinfobot](https://t.me/userinfobot), or use your group/channel id).
3. Copy the example config and fill it in:
   ```
   cp config.example.json config.json
   ```
4. Edit `config.json` with your token, chat id, and the alerts you want.

## Run

```
pip install -r requirements.txt
python bot.py
```

Leave it running and it checks prices on the interval you set.

## Run with Docker

```
docker build -t price-alert-bot .
docker run -d --restart always price-alert-bot
```

## Config example

```json
{
  "telegram": { "bot_token": "...", "chat_id": "..." },
  "vs_currency": "usd",
  "poll_interval_seconds": 60,
  "alerts": [
    { "coin": "bitcoin", "type": "above", "value": 70000 },
    { "coin": "ethereum", "type": "below", "value": 3000 },
    { "coin": "solana", "type": "percent_change_24h", "value": 5 }
  ]
}
```

## Notes

Coin names use CoinGecko ids (`bitcoin`, `ethereum`, `solana`, and so on). Add as many alerts as you want.
```
