import time
import json
import requests
import telebot
from threading import Thread
import os
from flask import Flask

def create_keep_alive():
    app = Flask(__name__)
    
    @app.route('/')
    def home():
        return "Bot is running!"
    
    def run():
        app.run(host='0.0.0.0', port=8080)
    
    Thread(target=run, daemon=True).start()

# Bot bilgileri
BOT_TOKEN = os.getenv("TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "1316760864"))  # Owner ID (sadece sen)
ALLOWED_USERS_FILE = "allowed_users.json"
DATA_FILE = "urls.json"  # URL'lerin saklanacağı JSON dosyası
INTERVAL = 300  # Ping atma süresi (saniye)

# Botu başlat
bot = telebot.TeleBot(BOT_TOKEN)

# JSON dosyaları otomatik oluşturulsun
def ensure_json_exists(file, default_data):
    """Eğer JSON dosyası yoksa, belirtilen varsayılan veriyle oluşturur."""
    if not os.path.exists(file):
        with open(file, "w") as f:
            json.dump(default_data, f, indent=4)

# Gerekli dosyaları oluştur
ensure_json_exists(ALLOWED_USERS_FILE, [OWNER_ID])
ensure_json_exists(DATA_FILE, [])

def load_users():
    """İzin verilen kullanıcıları yükler."""
    with open(ALLOWED_USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    """İzin verilen kullanıcıları kaydeder."""
    with open(ALLOWED_USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

def load_urls():
    """JSON dosyasından URL listesini yükler."""
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_urls(urls):
    """URL listesini JSON dosyasına kaydeder."""
    with open(DATA_FILE, "w") as f:
        json.dump(urls, f, indent=4)

def ping_url(url):
    """Belirtilen URL'ye ping atar."""
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
            print("⚠️ İzlenecek URL yok.")
        for url in urls:
            print(ping_url(url))
        time.sleep(INTERVAL)

if __name__ == "__main__":
    create_keep_alive()
    Thread(target=start_uptime_checker, daemon=True).start()
    print("✅ Bot çalışıyor...")
    bot.polling(none_stop=True)
