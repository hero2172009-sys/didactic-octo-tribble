import os
import time
import requests
from bs4 import BeautifulSoup
import telebot

# GitHub gizli alanlarından (Secrets) bilgileri alır
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
ARANAN_URUN = "esp32"

bot = telebot.TeleBot(BOT_TOKEN)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "tr-TR,tr;q=0.9"
}

def fiyat_temizle(fiyat_str):
    try:
        temiz = fiyat_str.replace('.', '').replace(',', '.').replace('TL', '').replace('₺', '').replace(' ', '')
        match = re.search(r'\d+\.?\d*', temiz)
        return float(match.group()) if match else None
    except:
        return None

def trendyol_ara():
    url = f"https://www.trendyol.com/sr?q={ARANAN_URUN}"
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            card = soup.select_one("div.p-card-wrppr")
            if card:
                title = card.select_one("span.prdct-desc-cntnr-name").text.strip()
                price = fiyat_temizle(card.select_one("div.prc-box-dscntrd, div.prc-box-sllng").text)
                link = "https://www.trendyol.com" + card.select_one("a").get("href")
                return price, title, link
    except:
        pass
    return float('inf'), "Bulunamadı", ""

def hepsiburada_ara():
    url = f"https://www.hepsiburada.com/ara?q={ARANAN_URUN}"
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            card = soup.select_one("li.search-item")
            if card:
                title = card.select_one("h3").text.strip()
                price = fiyat_temizle(card.select_one("div.price-value").text)
                link = "https://www.hepsiburada.com" + card.select_one("a").get("href")
                return price, title, link
    except:
        pass
    return float('inf'), "Bulunamadı", ""

print("Bulut taraması başlatılıyor...")
t_fiyat, t_ad, t_link = trendyol_ara()
h_fiyat, h_ad, h_link = hepsiburada_ara()

if t_fiyat < h_fiyat and t_fiyat != float('inf'):
    mesaj = f"🏆 **Trendyol Daha Ucuz!**\n\n📦 Ürün: {t_ad}\n💰 Fiyat: {t_fiyat:,.2f} TL\n🔗 [Ürüne Git]({t_link})"
    bot.send_message(CHAT_ID, mesaj, parse_mode="Markdown")
elif h_fiyat < t_fiyat and h_fiyat != float('inf'):
    mesaj = f"🏆 **Hepsiburada Daha Ucuz!**\n\n📦 Ürün: {h_ad}\n💰 Fiyat: {h_fiyat:,.2f} TL\n🔗 [Ürüne Git]({h_link})"
    bot.send_message(CHAT_ID, mesaj, parse_mode="Markdown")
else:
    print("Fiyat avantajı bulunamadı.")
import re
