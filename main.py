import time
import json
import requests
import telebot
from threading import Thread
import os

# Render'dan ENV değişkenini al
BOT_TOKEN = os.getenv("TOKEN")  # Render'daki Environment Variables'dan TOKEN alınır
OWNER_ID = 1316760864  # Owner ID (sadece Berat)

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN bulunamadı! Render'da Environment Variables'a 'TOKEN' eklediğinizden emin olun.")

data_file = "urls.json"  # URL'lerin saklanacağı JSON dosyası
interval = 300  # Ping atma süresi (saniye)
allowed_users = [OWNER_ID]  # İşlem yapabilecek kullanıcılar

bot = telebot.TeleBot(BOT_TOKEN)

# Webhook'u temizle (Çakışmayı önler)
bot.remove_webhook()

# urls.json dosyası yoksa oluştur
if not os.path.exists(data_file):
    with open(data_file, "w") as f:
        json.dump([], f)

def load_urls():
    """JSON dosyasından URL listesini yükler."""
    try:
        with open(data_file, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_urls(urls):
    """URL listesini JSON dosyasına kaydeder."""
    with open(data_file, "w") as f:
        json.dump(urls, f, indent=4)

def ping_url(url):
    """Belirtilen URL'ye istek atar ve durumu kontrol eder."""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return f"✅ {url} - UP"
        else:
            return f"⚠️ {url} - ERROR {response.status_code}"
    except requests.RequestException:
        return f"❌ {url} - DOWN"

def start_uptime_checker():
    """URL listesine sürekli ping atan fonksiyon."""
    while True:
        urls = load_urls()
        if not urls:
            print("⚠️ İzlenecek URL yok. Lütfen bir URL ekleyin.")
        for url in urls:
            print(ping_url(url))
        time.sleep(interval)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 Merhaba! Bu bot uptime takibi yapar. /help komutu ile kullanım talimatlarını görebilirsiniz.")

@bot.message_handler(commands=['list'])
def list_urls(message):
    if message.chat.id not in allowed_users:
        bot.reply_to(message, "🚫 Bu komutu kullanamazsınız!")
        return
    urls = load_urls()
    if urls:
        bot.reply_to(message, "📌 İzlenen URL'ler:\n" + "\n".join(urls))
    else:
        bot.reply_to(message, "⚠️ İzlenecek URL yok.")

if __name__ == "__main__":
    # Uptime checker'ı farklı bir thread'de başlat
    Thread(target=start_uptime_checker, daemon=True).start()
    print("✅ Bot çalışıyor...")
    bot.polling(none_stop=True)
