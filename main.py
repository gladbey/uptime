import time
import json
import requests
import telebot
from threading import Thread
import os

# Render Environment Variables'dan bot token'ını al
BOT_TOKEN = os.getenv("TOKEN")  
OWNER_ID = int(os.getenv("OWNER_ID", "1316760864"))  # Owner ID (sadece sen)
ALLOWED_USERS_FILE = "allowed_users.json"
DATA_FILE = "urls.json"  # URL'lerin saklanacağı JSON dosyası
INTERVAL = 300  # Ping atma süresi (saniye)

# Botu başlat
bot = telebot.TeleBot(BOT_TOKEN)

# Webhook'u temizle (Polling çakışmasını önler)
bot.remove_webhook()

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
    """Render'daki URL'leri sürekli ping atan fonksiyon."""
    while True:
        urls = load_urls()
        if not urls:
            print("⚠️ İzlenecek URL yok.")
        for url in urls:
            print(ping_url(url))
        time.sleep(INTERVAL)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 Merhaba! Bu bot uptime takibi yapar. /help ile komutları görebilirsiniz.")

@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = """
🛠 **Komut Listesi**:
/add [URL] - Yeni bir URL ekler
/remove [URL] - Bir URL'yi kaldırır
/list - İzlenen URL'leri listeler
/adduser [ID] - Kullanıcı ekler (Sadece owner)
/removeuser [ID] - Kullanıcıyı kaldırır (Sadece owner)
/users - Yetkili kullanıcıları listeler
    """
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['list'])
def list_urls(message):
    if message.chat.id not in load_users():
        bot.reply_to(message, "🚫 Bu komutu kullanamazsınız!")
        return
    urls = load_urls()
    if urls:
        bot.reply_to(message, "📌 İzlenen URL'ler:\n" + "\n".join(urls))
    else:
        bot.reply_to(message, "⚠️ İzlenecek URL yok.")

@bot.message_handler(commands=['add'])
def add_command(message):
    if message.chat.id not in load_users():
        bot.reply_to(message, "🚫 Bu komutu kullanamazsınız!")
        return
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "⚠️ Kullanım: /add [URL]")
        return
    url = parts[1]
    urls = load_urls()
    if url not in urls:
        urls.append(url)
        save_urls(urls)
        bot.reply_to(message, f"✅ {url} eklendi!")
    else:
        bot.reply_to(message, "⚠️ Bu URL zaten listede.")

@bot.message_handler(commands=['remove'])
def remove_command(message):
    if message.chat.id not in load_users():
        bot.reply_to(message, "🚫 Bu komutu kullanamazsınız!")
        return
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "⚠️ Kullanım: /remove [URL]")
        return
    url = parts[1]
    urls = load_urls()
    if url in urls:
        urls.remove(url)
        save_urls(urls)
        bot.reply_to(message, f"✅ {url} kaldırıldı!")
    else:
        bot.reply_to(message, "⚠️ Bu URL listede yok.")

@bot.message_handler(commands=['adduser'])
def add_user(message):
    if message.chat.id != OWNER_ID:
        bot.reply_to(message, "🚫 Bu komutu sadece owner kullanabilir!")
        return
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "⚠️ Kullanım: /adduser [ID]")
        return
    user_id = int(parts[1])
    users = load_users()
    if user_id not in users:
        users.append(user_id)
        save_users(users)
        bot.reply_to(message, f"✅ Kullanıcı {user_id} eklendi!")
    else:
        bot.reply_to(message, "⚠️ Bu kullanıcı zaten ekli.")

@bot.message_handler(commands=['removeuser'])
def remove_user(message):
    if message.chat.id != OWNER_ID:
        bot.reply_to(message, "🚫 Bu komutu sadece owner kullanabilir!")
        return
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "⚠️ Kullanım: /removeuser [ID]")
        return
    user_id = int(parts[1])
    users = load_users()
    if user_id in users:
        users.remove(user_id)
        save_users(users)
        bot.reply_to(message, f"✅ Kullanıcı {user_id} kaldırıldı!")
    else:
        bot.reply_to(message, "⚠️ Bu kullanıcı listede yok.")

@bot.message_handler(commands=['users'])
def list_users(message):
    if message.chat.id != OWNER_ID:
        bot.reply_to(message, "🚫 Bu komutu sadece owner kullanabilir!")
        return
    users = load_users()
    bot.reply_to(message, "👥 Yetkili Kullanıcılar:\n" + "\n".join(map(str, users)))

if __name__ == "__main__":
    # Webhook'u kaldırıp, Uptime Checker başlat
    bot.remove_webhook()
    Thread(target=start_uptime_checker, daemon=True).start()
    print("✅ Bot çalışıyor...")
    bot.polling(none_stop=True, skip_pending=True)
