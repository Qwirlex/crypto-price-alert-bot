import json
import time
import logging

import requests

COINGECKO_URL = "https://api.coingecko.com/api/v3/simple/price"
TELEGRAM_URL = "https://api.telegram.org/bot{token}/sendMessage"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("price-alert")


def load_config(path="config.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_prices(coin_ids, vs_currency):
    params = {
        "ids": ",".join(coin_ids),
        "vs_currencies": vs_currency,
        "include_24hr_change": "true",
    }
    resp = requests.get(COINGECKO_URL, params=params, timeout=15)
    resp.raise_for_status()
    return resp.json()


def send_telegram(token, chat_id, text):
    resp = requests.post(
        TELEGRAM_URL.format(token=token),
        data={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
        timeout=15,
    )
    resp.raise_for_status()


def alert_triggered(alert, price_data, vs_currency):
    price = price_data.get(vs_currency)
    change = price_data.get(f"{vs_currency}_24h_change")
    if price is None:
        return False
    kind = alert["type"]
    value = alert["value"]
    if kind == "above":
        return price > value
    if kind == "below":
        return price < value
    if kind == "percent_change_24h":
        return change is not None and abs(change) >= value
    log.warning("unknown alert type: %s", kind)
    return False


def format_message(alert, price_data, vs_currency):
    price = price_data.get(vs_currency)
    change = price_data.get(f"{vs_currency}_24h_change")
    coin = alert["coin"]
    cur = vs_currency.upper()
    kind = alert["type"]
    if kind == "above":
        return f"\U0001F514 <b>{coin}</b> is above {alert['value']} {cur}\nNow: {price} {cur}"
    if kind == "below":
        return f"\U0001F514 <b>{coin}</b> is below {alert['value']} {cur}\nNow: {price} {cur}"
    if kind == "percent_change_24h":
        return f"\U0001F514 <b>{coin}</b> moved {change:.2f}% in 24h\nNow: {price} {cur}"
    return f"\U0001F514 Alert on {coin}: {price} {cur}"


def main():
    config = load_config()
    tg = config["telegram"]
    vs = config.get("vs_currency", "usd")
    interval = config.get("poll_interval_seconds", 60)
    alerts = config["alerts"]
    coin_ids = sorted({a["coin"] for a in alerts})

    # remembers which alerts already fired so we do not spam the same one.
    # an alert can fire again only after its condition goes false and then true again.
    fired = {}

    log.info("watching %d coins, polling every %ds", len(coin_ids), interval)
    while True:
        try:
            prices = get_prices(coin_ids, vs)
            for i, alert in enumerate(alerts):
                data = prices.get(alert["coin"], {})
                triggered = alert_triggered(alert, data, vs)
                if triggered and not fired.get(i):
                    msg = format_message(alert, data, vs)
                    send_telegram(tg["bot_token"], tg["chat_id"], msg)
                    log.info("sent alert: %s", msg.replace("\n", " | "))
                    fired[i] = True
                elif not triggered:
                    fired[i] = False
        except requests.RequestException as e:
            log.error("request failed: %s", e)
        except Exception as e:  # keep the loop alive on anything unexpected
            log.exception("unexpected error: %s", e)
        time.sleep(interval)


if __name__ == "__main__":
    main()
