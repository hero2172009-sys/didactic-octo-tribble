import os
import re
import requests
from bs4 import BeautifulSoup
import telebot

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# Takip edilecek ürünler
ARANAN_URUNLER = ["esp32 s3", "3.5 inch spi ekran"]

bot = telebot.TeleBot(BOT_TOKEN)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
        " like Gecko) Chrome/126.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "tr-TR,tr;q=0.9",
}

def fiyat_temizle(fiyat_str):
    try:
        temiz = fiyat_str.replace(".", "").replace(",", ".").replace("TL", "").replace("₺", "").strip()
        match = re.search(r"\d+\.?\d*", temiz)
        return float(match.group()) if match else None
    except:
        return None

def trendyol_ara(urun):
    url = f"https://www.trendyol.com/sr?q={urun.replace(' ', '+')}"
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            # En genel kart seçicileri kullanıyoruz
            card = soup.select_one("div.p-card-wrppr")
            if card:
                title = card.select_one("span.prdct-desc-cntnr-name").text.strip()
                # İndirimli veya normal fiyat etiketlerini yakala
                price_text = card.select_one("div.prc-box-dscntrd, div.prc-box-sllng").text
                price = fiyat_temizle(price_text)
                link = "https://www.trendyol.com" + card.select_one("a").get("href")
                return price, title, link
    except:
        pass
    return float("inf"), "Bulunamadı", ""

def hepsiburada_ara(urun):
    url = f"https://www.hepsiburada.com/ara?q={urun.replace(' ', '+')}"
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            # Hepsiburada liste kartını yakala
            card = soup.select_one("li.search-item")
            if card:
                title = card.select_one("h3").text.strip()
                price = fiyat_temizle(card.select_one("div[data-test-id='price-current-price']").text)
                link = "https://www.hepsiburada.com" + card.select_one("a").get("href")
                return price, title, link
    except:
        pass
    return float("inf"), "Bulunamadı", ""

# Raporu hazırla
rapor = "🔍 **Güncel Fiyat Raporu:**\n"

for urun in ARANAN_URUNLER:
    t_fiyat, t_ad, t_link = trendyol_ara(urun)
    h_fiyat, h_ad, h_link = hepsiburada_ara(urun)
    
    rapor += f"\n📦 **{urun.upper()}**\n"
    
    if t_fiyat == float("inf") and h_fiyat == float("inf"):
        rapor += "❌ Ürün bulunamadı.\n"
    else:
        if t_fiyat <= h_fiyat:
            rapor += f"🏆 En Ucuz: **Trendyol** - {t_fiyat:,.2f} TL\n🔗 [Ürüne Git]({t_link})\n"
        else:
            rapor += f"🏆 En Ucuz: **Hepsiburada** - {h_fiyat:,.2f} TL\n🔗 [Ürüne Git]({h_link})\n"

# Raporu gönder
try:
    bot.send_message(CHAT_ID, rapor, parse_mode="Markdown")
except Exception as e:
    print(f"Hata: {e}")
