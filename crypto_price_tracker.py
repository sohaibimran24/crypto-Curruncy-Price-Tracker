# ============================================
# Crypto Price Tracker
# Author: Muhammad Sohaib Imran
# FAST-NUCES, Lahore | FinTech
# Uses: CoinGecko Free API (no key needed)
# Install: pip install requests
# ============================================

import requests
import os
import time
from datetime import datetime


BASE_URL = "https://api.coingecko.com/api/v3"

SUPPORTED_COINS = {
    "1": "bitcoin",
    "2": "ethereum",
    "3": "binancecoin",
    "4": "solana",
    "5": "ripple",
    "6": "cardano",
    "7": "dogecoin",
    "8": "polkadot",
    "9": "chainlink",
    "10": "litecoin"
}

COIN_SYMBOLS = {
    "bitcoin": "BTC",
    "ethereum": "ETH",
    "binancecoin": "BNB",
    "solana": "SOL",
    "ripple": "XRP",
    "cardano": "ADA",
    "dogecoin": "DOGE",
    "polkadot": "DOT",
    "chainlink": "LINK",
    "litecoin": "LTC"
}


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header():
    print("\n" + "=" * 60)
    print("           📈 CRYPTO PRICE TRACKER")
    print("           Muhammad Sohaib Imran | FAST-NUCES")
    print("           Powered by CoinGecko API")
    print("=" * 60)


def format_number(num):
    """Format large numbers with B/M suffix."""
    if num >= 1_000_000_000:
        return f"${num/1_000_000_000:.2f}B"
    elif num >= 1_000_000:
        return f"${num/1_000_000:.2f}M"
    else:
        return f"${num:,.2f}"


def get_price_arrow(change):
    """Return colored arrow based on price change."""
    if change > 0:
        return f"▲ +{change:.2f}%"
    elif change < 0:
        return f"▼ {change:.2f}%"
    else:
        return f"→ {change:.2f}%"


def fetch_top_coins(currency="usd", limit=10):
    """Fetch top cryptocurrencies by market cap."""
    try:
        url = f"{BASE_URL}/coins/markets"
        params = {
            "vs_currency": currency,
            "order": "market_cap_desc",
            "per_page": limit,
            "page": 1,
            "sparkline": False,
            "price_change_percentage": "24h"
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        print("\n  ❌ No internet connection. Please check your network.")
        return None
    except requests.exceptions.Timeout:
        print("\n  ❌ Request timed out. Please try again.")
        return None
    except Exception as e:
        print(f"\n  ❌ Error fetching data: {e}")
        return None


def fetch_coin_details(coin_id):
    """Fetch detailed info for a specific coin."""
    try:
        url = f"{BASE_URL}/coins/{coin_id}"
        params = {"localization": False, "sparkline": False}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"\n  ❌ Error fetching coin details: {e}")
        return None


def fetch_historical_prices(coin_id, days=7):
    """Fetch historical price data."""
    try:
        url = f"{BASE_URL}/coins/{coin_id}/market_chart"
        params = {"vs_currency": "usd", "days": days}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"\n  ❌ Error fetching historical data: {e}")
        return None


def display_top_coins(coins):
    """Display top cryptocurrencies in a table."""
    if not coins:
        return

    print(f"\n  {'#':<4} {'Coin':<18} {'Price (USD)':>14} {'24h Change':>12} {'Market Cap':>14} {'Volume':>12}")
    print("  " + "─" * 76)

    for i, coin in enumerate(coins, 1):
        name = f"{coin['name']} ({coin['symbol'].upper()})"[:17]
        price = f"${coin['current_price']:,.4f}" if coin['current_price'] < 1 else f"${coin['current_price']:,.2f}"
        change = coin.get('price_change_percentage_24h') or 0
        arrow = get_price_arrow(change)
        market_cap = format_number(coin['market_cap']) if coin['market_cap'] else "N/A"
        volume = format_number(coin['total_volume']) if coin['total_volume'] else "N/A"

        print(f"  {i:<4} {name:<18} {price:>14} {arrow:>12} {market_cap:>14} {volume:>12}")

    print("  " + "─" * 76)
    print(f"\n  🕐 Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def display_coin_details(coin_id):
    """Display detailed info for a specific coin."""
    print(f"\n  ⏳ Fetching details for {coin_id}...")
    data = fetch_coin_details(coin_id)
    if not data:
        return

    market = data.get('market_data', {})

    print(f"\n  {'='*50}")
    print(f"  🪙  {data['name']} ({data['symbol'].upper()})")
    print(f"  {'='*50}")
    print(f"  Current Price     : ${market['current_price'].get('usd', 0):,.4f}")
    print(f"  24h High          : ${market['high_24h'].get('usd', 0):,.4f}")
    print(f"  24h Low           : ${market['low_24h'].get('usd', 0):,.4f}")
    print(f"  24h Change        : {get_price_arrow(market['price_change_percentage_24h'] or 0)}")
    print(f"  7d Change         : {get_price_arrow(market.get('price_change_percentage_7d') or 0)}")
    print(f"  Market Cap        : {format_number(market['market_cap'].get('usd', 0))}")
    print(f"  24h Volume        : {format_number(market['total_volume'].get('usd', 0))}")
    print(f"  Circulating Supply: {market['circulating_supply']:,.0f} {data['symbol'].upper()}")
    ath = market['ath'].get('usd', 0)
    print(f"  All Time High     : ${ath:,.4f}")
    print(f"  {'='*50}")

    desc = data.get('description', {}).get('en', '')
    if desc:
        print(f"\n  📝 About: {desc[:200]}...")


def display_mini_chart(prices, coin_name):
    """Display a simple ASCII price chart."""
    if not prices or len(prices) < 2:
        return

    values = [p[1] for p in prices]
    min_val = min(values)
    max_val = max(values)
    height = 8
    width = min(len(values), 40)

    # Sample prices to fit width
    step = len(values) // width
    sampled = [values[i] for i in range(0, len(values), max(1, step))][:width]

    print(f"\n  📊 {coin_name} — Last 7 Days Price Chart")
    print(f"  High: ${max_val:,.2f}   Low: ${min_val:,.2f}")
    print()

    for row in range(height, 0, -1):
        line = "  |"
        for val in sampled:
            normalized = (val - min_val) / (max_val - min_val) if max_val != min_val else 0.5
            bar_height = int(normalized * height)
            line += "█" if bar_height >= row else " "
        print(line)

    print("  +" + "─" * len(sampled))
    print(f"  {'7 days ago':<20} {'Today':>20}")


def set_price_alert(coins):
    """Set a price alert for a cryptocurrency."""
    print("\n  🔔 SET PRICE ALERT")
    print("  " + "-" * 30)
    print("  Available coins:")
    for key, coin in SUPPORTED_COINS.items():
        print(f"  {key}. {coin.capitalize()} ({COIN_SYMBOLS[coin]})")

    choice = input("\n  Select coin (1-10): ").strip()
    if choice not in SUPPORTED_COINS:
        print("  ❌ Invalid choice!")
        return

    coin_id = SUPPORTED_COINS[choice]
    coin_data = next((c for c in coins if c['id'] == coin_id), None)

    if not coin_data:
        print("  ❌ Coin data not available!")
        return

    current = coin_data['current_price']
    print(f"\n  Current {coin_id.capitalize()} price: ${current:,.4f}")

    try:
        target = float(input("  Enter target price ($): "))
    except ValueError:
        print("  ❌ Invalid price!")
        return

    direction = "above" if target > current else "below"
    print(f"\n  ✅ Alert set! Monitoring {coin_id.capitalize()} until it goes {direction} ${target:,.4f}")
    print("  Press Ctrl+C to stop monitoring...\n")

    checks = 0
    try:
        while True:
            fresh = fetch_top_coins(limit=10)
            if fresh:
                fresh_coin = next((c for c in fresh if c['id'] == coin_id), None)
                if fresh_coin:
                    price = fresh_coin['current_price']
                    checks += 1
                    print(f"  [{checks}] {coin_id.capitalize()}: ${price:,.4f} | Target: ${target:,.4f}", end='\r')

                    if (direction == "above" and price >= target) or \
                       (direction == "below" and price <= target):
                        print(f"\n\n  🚨 ALERT! {coin_id.capitalize()} hit ${price:,.4f}!")
                        break

            time.sleep(30)  # Check every 30 seconds
    except KeyboardInterrupt:
        print("\n\n  ⛔ Alert monitoring stopped.")


def main_menu():
    print("\n  MENU")
    print("  " + "-" * 35)
    print("  1. 📊 View Top 10 Cryptocurrencies")
    print("  2. 🔍 Coin Details")
    print("  3. 📈 7-Day Price Chart")
    print("  4. 🔔 Set Price Alert")
    print("  5. 🔄 Auto-Refresh (every 60s)")
    print("  0. 🚪 Exit")
    print("  " + "-" * 35)


def main():
    clear_screen()
    print_header()
    print("\n  Welcome! Fetching live crypto data...\n")

    coins = fetch_top_coins()

    while True:
        clear_screen()
        print_header()
        main_menu()

        choice = input("\n  Enter choice: ").strip()

        if choice == "1":
            print("\n  ⏳ Fetching live prices...")
            coins = fetch_top_coins()
            if coins:
                display_top_coins(coins)

        elif choice == "2":
            print("\n  Available coins:")
            for key, coin in SUPPORTED_COINS.items():
                print(f"  {key}. {coin.capitalize()} ({COIN_SYMBOLS[coin]})")
            sel = input("\n  Select coin (1-10): ").strip()
            if sel in SUPPORTED_COINS:
                display_coin_details(SUPPORTED_COINS[sel])
            else:
                print("  ❌ Invalid choice!")

        elif choice == "3":
            print("\n  Available coins:")
            for key, coin in SUPPORTED_COINS.items():
                print(f"  {key}. {coin.capitalize()} ({COIN_SYMBOLS[coin]})")
            sel = input("\n  Select coin (1-10): ").strip()
            if sel in SUPPORTED_COINS:
                coin_id = SUPPORTED_COINS[sel]
                print(f"\n  ⏳ Fetching 7-day data for {coin_id}...")
                hist = fetch_historical_prices(coin_id, days=7)
                if hist:
                    display_mini_chart(hist['prices'], coin_id.capitalize())
            else:
                print("  ❌ Invalid choice!")

        elif choice == "4":
            if not coins:
                coins = fetch_top_coins()
            if coins:
                set_price_alert(coins)

        elif choice == "5":
            print("\n  🔄 Auto-refresh mode. Press Ctrl+C to stop.\n")
            try:
                while True:
                    clear_screen()
                    print_header()
                    coins = fetch_top_coins()
                    if coins:
                        display_top_coins(coins)
                    print("\n  🔄 Refreshing in 60 seconds... (Ctrl+C to stop)")
                    time.sleep(60)
            except KeyboardInterrupt:
                print("\n\n  ⛔ Auto-refresh stopped.")

        elif choice == "0":
            print("\n  📈 Happy Trading!")
            print("  — Muhammad Sohaib Imran | FAST-NUCES\n")
            break

        else:
            print("\n  ❌ Invalid choice!")

        input("\n  Press Enter to continue...")


if __name__ == "__main__":
    main()
