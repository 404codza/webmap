# Codza tarafından oluşturuldu.

import requests
import difflib
import threading
from concurrent.futures import ThreadPoolExecutor
from colorama import Fore, Style, init
import os

init(autoreset=True)

# =============== AYARLAR ===============
url = "http://example.com/"           # Hedef site (sonunda / olmalı)
wordlist = "common.txt"               # Wordlist dosya adı
output_file = "found.txt"             # Bulunanlar buraya yazılır
max_threads = 20                      # Aynı anda çalışan thread sayısı
silent_mode = False                   # True yaparsan sadece bulunanları yazar
similarity_threshold = 0.95           # Benzerlik eşiği (eski 0.9'dan daha esnek)

headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 11; Termux)"
}

lock = threading.Lock()

# =========== 404 REFERANSI ============
def get_404_reference():
    try:
        test_path = "/thispagedoesnotexist987654321"
        response = requests.get(url.rstrip("/") + test_path, headers=headers, timeout=5)
        return response.status_code, response.text.strip().lower()
    except Exception as e:
        print(Fore.RED + f"[!] 404 referansı alınamadı: {e}\n")
        return 404, ""

# =========== BENZERLİK HESABI ============
def similarity(a, b):
    return difflib.SequenceMatcher(None, a, b).ratio()

# =========== TEK TEK PATH KONTROL ============
def check_path(path):
    path = path.strip()
    if not path.startswith("/"):
        path = "/" + path
    full_url = url.rstrip("/") + path

    try:
        response = requests.get(full_url, headers=headers, timeout=5)
        status_code = response.status_code
        content = response.text.strip().lower()
        sim_ratio = similarity(content[:1500], not_found_content[:1500])

        if status_code == 404 or (status_code == not_found_status and sim_ratio > similarity_threshold):
            if not silent_mode:
                print(Fore.RED + f"[X] Yok: {full_url}\n")
            return

        if status_code == 200 and sim_ratio <= similarity_threshold:
            print(Fore.GREEN + f"[✓] Bulundu: {full_url}\n")
            with lock:
                with open(output_file, "a") as f:
                    f.write(full_url + "\n")
            return

        if not silent_mode:
            print(Fore.YELLOW + f"[?] Belirsiz: {full_url} (Status: {status_code})\n")

    except requests.RequestException as e:
        if not silent_mode:
            print(Fore.MAGENTA + f"[!] Hata: {full_url} | {e}\n")

# =============== ANA TARAYICI ===============
def main():
    if not os.path.exists(wordlist):
        print(Fore.RED + f"[!] Wordlist dosyası bulunamadı: {wordlist}")
        return

    with open(wordlist, "r", encoding="utf-8") as file:
        paths = file.readlines()

    print(Fore.CYAN + f"[i] {len(paths)} yol taranıyor...\n")

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        executor.map(check_path, paths)

# =============== GİRİŞ NOKTASI ===============
if __name__ == "__main__":
    not_found_status, not_found_content = get_404_reference()

    print(Fore.BLUE + "[i] 404 referansı alındı. Tarama başlıyor...\n")

    main()

    print(Fore.CYAN + f"\n[i] Tarama tamamlandı. Sonuçlar -> {output_file}\n")
