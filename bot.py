import os
import re
import time
from bs4 import BeautifulSoup
import requests
import telebot

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# Takip etmek istediğin ürünlerin listesi
ARANAN_URUNLER = ["esp32 s3", "3.5 inch spi ekran"]

bot = telebot.TeleBot(BOT_TOKEN)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
        " like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "tr-TR,tr;q=0.9",
}


def fiyat_temizle(fiyat_str):
  try:
    temiz = (
        fiyat_str.replace(".", "")
        .replace(",", ".")
        .replace("TL", "")
        .replace("₺", "")
        .replace(" ", "")
    )
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
      card = soup.select_one("div.p-card-wrppr")
      if card:
        title = card.select_one("span.prdct-desc-cntnr-name").text.strip()
        price = fiyat_temizle(
            card.select_one("div.prc-box-dscntrd, div.prc-box-sllng").text
        )
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
      card = soup.select_one("li.search-item")
      if card:
        title = card.select_one("h3").text.strip()
        price = fiyat_temizle(card.select_one("div.price-value").text)
        link = "https://www.hepsiburada.com" + card.select_one("a").get("href")
        return price, title, link
  except:
    pass
  return float("inf"), "Bulunamadı", ""


print("Çoklu ürün taraması başlatılıyor...")
rapor_mesaji = "🔍 **Güncel Fiyat Raporu:**\n"

for urun in ARANAN_URUNLER:
  t_fiyat, t_ad, t_link = trendyol_ara(urun)
  h_fiyat, h_ad, h_link = hepsiburada_ara(urun)

  rapor_mesaji += f"\n📦 **{urun.upper()}**\n"

  if t_fiyat == float("inf") and h_fiyat == float("inf"):
    rapor_mesaji += "❌ Hiçbir sitede ürün bulunamadı.\n"
    continue

  if t_fiyat <= h_fiyat:
    en_ucuz_fiyat = t_fiyat
    en_ucuz_site = "Trendyol"
    en_ucuz_link = t_link
    en_ucuz_ad = t_ad
  else:
    en_ucuz_fiyat = h_fiyat
    en_ucuz_site = "Hepsiburada"
    en_ucuz_link = h_link
    en_ucuz_ad = h_ad

  rapor_mesaji += (
      f"🏆 En Ucuz: **{en_ucuz_site}** - {en_ucuz_fiyat:,.2f} TL\n🔗"
      f" [Ürüne Git]({en_ucuz_link})\n"
  )

# Telegram'a raporu gönder
bot.send_message(CHAT_ID, rapor_mesaji, parse_mode="Markdown")
print("Rapor başarıyla gönderildi.")
