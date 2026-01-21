import requests
from bs4 import BeautifulSoup
import csv
import time
import random
import logging
import re

# ================== НАСТРОЙКИ ==================
BASE_URL = "https://krisha.kz/prodazha/kvartiry"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "ru-RU,ru;q=0.9"
}
CSV_FILE = "results.csv"
LOG_FILE = "parser.log"

# ================== ЛОГГЕР ==================
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    encoding="utf-8"
)

def log(msg, level="info"):
    print(msg)
    if level == "info":
        logging.info(msg)
    elif level == "warning":
        logging.warning(msg)
    elif level == "error":
        logging.error(msg)
    for h in logging.getLogger().handlers:
        h.flush()

# ================== GET HTML ==================
def get_html(city_slug, page, rooms=None):
    params = {"page": page}
    if rooms:
        params["das[flat.rooms]"] = rooms
    try:
        r = requests.get(f"{BASE_URL}/{city_slug}/", headers=HEADERS, params=params, timeout=15)
        r.raise_for_status()
        return r.text
    except Exception as e:
        log(f"Ошибка запроса страницы {page}: {e}", level="error")
        return None

# ================== ПАРСИНГ ОБЪЯВЛЕНИЙ ==================
def get_ads(html):
    soup = BeautifulSoup(html, "lxml")
    return soup.select("div.a-card")

def parse_ad(ad):
    try:
        title_tag = ad.select_one(".a-card__title")
        price_tag = ad.select_one(".a-card__price")
        address_tag = ad.select_one(".a-card__subtitle")
        link_tag = ad.select_one("a.a-card__link")

        title = title_tag.get_text(strip=True) if title_tag else ""
        price_raw = price_tag.get_text(strip=True) if price_tag else ""
        price = re.sub(r"[^\d]", "", price_raw)
        price = f"{int(price):,}".replace(",", " ") if price else ""

        address = address_tag.get_text(strip=True) if address_tag else ""
        link = "https://krisha.kz" + link_tag.get("href") if link_tag else ""

        # Разделяем адрес на город и улицу
        city = "Aktobe"  # фиксируем город
        street = address.replace(city, "").strip(", — ")

        rooms_match = re.search(r"(\d+)-комнат", title)
        rooms = rooms_match.group(1) if rooms_match else ""

        square_match = re.search(r"([\d,.]+) ?м²", title)
        square = square_match.group(1) if square_match else ""

        floor_match = re.search(r"(\d+/\d+) этаж", title)
        floor = floor_match.group(1) if floor_match else ""

        return {
            "title": title,
            "price": price,
            "city": city,
            "street": street,
            "rooms": rooms,
            "square_m2": square,
            "floor": floor,
            "link": link
        }
    except Exception as e:
        log(f"Ошибка парсинга объявления: {e}", level="warning")
        return None

# ================== СОХРАНЕНИЕ CSV ==================
def save_csv(data):
    if not data:
        log("Нет данных для сохранения.", level="warning")
        return
    with open(CSV_FILE, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["title","price","city","street","rooms","square_m2","floor","link"],
            delimiter=";",            # Excel-friendly разделитель
            quoting=csv.QUOTE_ALL
        )
        writer.writeheader()
        writer.writerows(data)
    log(f"Данные сохранены в {CSV_FILE} | Всего: {len(data)}")

# ================== MAIN ==================
def main():
    print("🚀 KRISHA PARSER START")
    city_slug = "aktobe"
    rooms = input("Количество комнат (Enter — любые): ").strip()
    rooms = rooms if rooms else None

    log(f"СТАРТ | Город: {city_slug} | Комнат: {rooms}")
    results = []

    page = 1
    while True:
        log(f"📄 Парсим страницу {page}")
        html = get_html(city_slug, page, rooms)
        if not html:
            log(f"❌ Страница {page} недоступна", level="error")
            break

        ads = get_ads(html)
        if not ads:
            log(f"❌ Объявления на странице {page} не найдены. Парсинг завершен.")
            break

        log(f"🔎 Найдено {len(ads)} объявлений на странице {page}")

        for ad_block in ads:
            data = parse_ad(ad_block)
            if data:
                results.append(data)
                log(f"✔ {data['title']} | {data['price']} | {data['street']}")

            time.sleep(random.uniform(0.5, 1.0))

        page += 1
        time.sleep(random.uniform(1.5, 2.5))

    save_csv(results)
    log("🏁 ФИНИШ")

if __name__ == "__main__":
    main()
