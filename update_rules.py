import requests
import os
from datetime import datetime

# Настройки
SOURCE_URL = "https://raw.githubusercontent.com/Internet-Helper/GeoHideDNS/refs/heads/main/hosts/hosts"
CUSTOM_FILE = "custom_domains.txt"
OUTPUT_FILE = "my_ready_rules.txt"

# Ключевые слова для поиска (ограничено для лимита в 100 правил)
KEYWORDS = [
    "openai", "chatgpt", "oaistatic", "oaiusercontent", 
    "google", "gemini", "googleapis", "withgoogle", "pki.goog", "notebooklm", 
    "grok", "x.ai"
]

def main():
    unique_domains = set()
    now = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    
    personal_rules = []
    auto_rules = []

    # 1. Читаем твой файл custom_domains.txt
    if os.path.exists(CUSTOM_FILE):
        with open(CUSTOM_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip().lower()
                if not line or line.startswith(('#', '!', '0.0.0.0')): continue
                
                parts = line.split()
                if len(parts) >= 2:
                    ip = parts[0]
                    domain = parts[1]
                    if domain not in unique_domains:
                        unique_domains.add(domain)
                        personal_rules.append(f"||{domain}^$dnsrewrite={ip}")

    # 2. Читаем файл из интернета и берем IP оттуда
    try:
        response = requests.get(SOURCE_URL)
        if response.status_code == 200:
            lines = response.text.splitlines()
            for line in lines:
                line = line.strip().lower()
                if not line or line.startswith(('#', '0.0.0.0')): continue
                
                parts = line.split()
                if len(parts) >= 2:
                    # Извлекаем данные: первый элемент - IP, второй - домен
                    ip = parts[0]
                    domain = parts[1].replace("http://", "").replace("https://", "").split('/')[0]
                    
                    # Фильтруем по ключевым словам и следим за лимитом в 100 штук
                    if any(key in domain for key in KEYWORDS):
                        if domain not in unique_domains and len(unique_domains) < 100:
                            unique_domains.add(domain)
                            auto_rules.append(f"||{domain}^$dnsrewrite={ip}")
    except Exception as e:
        print(f"Ошибка: {e}")

    # 3. Формируем итоговый файл
    total = len(unique_domains)
    header = [
        f"! AI Unlocker Rules",
        f"! Обновлено: {now}",
        f"! Всего правил: {total} из 100",
        f"! Автоматически подставлены IP из источника",
        ""
    ]

    content = header + ["! --- ЛИЧНЫЕ ---"] + personal_rules + ["", "! --- АВТО ---"] + auto_rules

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(content))
    
    print(f"Готово! Сгенерировано правил: {total}")

if __name__ == "__main__":
    main()
