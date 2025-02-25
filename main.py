import time
import json
import requests
import telebot
from threading import Thread
import os

# Bot bilgileri
BOT_TOKEN = "7700764678:AAE_wWzg68yjcf-xFOsAWIy5Sb6JdhVSUc4"
OWNER_ID = 1316760864  # Owner ID (sadece )

data_file = "urls.json"  # URL'lerin saklanacağı JSON dosyası
interval = 300  # Ping atma süresi (saniye)
allowed_users = [OWNER_ID]  # İşlem yapabilecek kullanıcılar

bot = telebot.TeleBot(BOT_TOKEN)

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

def add_url(url):
    """Yeni bir URL ekler."""
    urls = load_urls()
    if url not in urls:
        urls.append(url)
        save_urls(urls)
        return f"✅ {url} eklendi!"
    else:
        return "⚠️ Bu URL zaten listede."

def remove_url(url):
    """Bir URL'yi listeden kaldırır."""
    urls = load_urls()
    if url in urls:
        urls.remove(url)
        save_urls(urls)
        return f"✅ {url} kaldırıldı!"
    else:
        return "⚠️ Bu URL listede yok."

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 Merhaba! Bu bot uptime takibi yapar. /help komutu ile kullanım talimatlarını görebilirsiniz.")

@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = """
🛠 Komut Listesi:
/add [URL] - Yeni bir URL ekler
/remove [URL] - Bir URL'yi kaldırır
/list - İzlenen URL'leri listeler
/adduser [ID] - Yeni bir kullanıcı ekler (Sadece owner)
/removeuser [ID] - Kullanıcıyı kaldırır (Sadece owner)
    """
    bot.reply_to(message, help_text)

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

@bot.message_handler(commands=['add'])
def add_command(message):
    if message.chat.id not in allowed_users:
        bot.reply_to(message, "🚫 Bu komutu kullanamazsınız!")
        return
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "⚠️ Kullanım: /add [URL]")
        return
    url = parts[1]
    bot.reply_to(message, add_url(url))

@bot.message_handler(commands=['remove'])
def remove_command(message):
    if message.chat.id not in allowed_users:
        bot.reply_to(message, "🚫 Bu komutu kullanamazsınız!")
        return
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "⚠️ Kullanım: /remove [URL]")
        return
    url = parts[1]
    bot.reply_to(message, remove_url(url))

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
    if user_id not in allowed_users:
        allowed_users.append(user_id)
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
    if user_id in allowed_users:
        allowed_users.remove(user_id)
        bot.reply_to(message, f"✅ Kullanıcı {user_id} kaldırıldı!")
    else:
        bot.reply_to(message, "⚠️ Bu kullanıcı listede yok.")

if __name__ == "__main__":
    # Uptime checker'ı farklı bir thread'de başlat
    Thread(target=start_uptime_checker, daemon=True).start()
    print("✅ Bot çalışıyor...")
    bot.polling(none_stop=True)
