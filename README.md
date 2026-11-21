# jtdmcserver

Setup, deployment scripts, tooling, and player instructions for the Joe The Duck Minecraft server.

---

## Hardware Context

The server runs on a dedicated 4-core laptop with 8 GB of RAM and a mechanical hard drive.

To avoid slow disk I/O freezes and keep memory usage within the 8 GB limit:
- **Java Heap**: Capped at 3 GB (`-Xms3G -Xmx3G`) with G1GC parallel GC threads tuned for 4 cores.
- **RAMDisk**: The active world directory runs entirely in a 2 GB `tmpfs` partition (`noatime,nodiratime`).
- **World Sync**: An automated `systemd` timer rsyncs the world from the RAM disk to persistent disk storage every 5 minutes and on clean server shutdown.
- **In-Game Distances**: `view-distance=8`, `simulation-distance=6`.

---

## Repository Structure

```text
jtdmcserver/
├── test.mrpack               # Client modpack for Pinecone / Prism Launcher
├── mods.txt                  # Direct CDN and release URLs for all server mods
├── scripts/
│   ├── download_mods.sh      # Fetches all server mods into the mods directory
│   ├── build_mrpack.py       # Rebuilds test.mrpack with current mod URLs and overrides
│   ├── sync_world.sh         # RAMDisk mount, rsync to disk, and unmount handler
│   └── start.sh              # Server launch script with 3G G1GC tuning
├── systemd/
│   ├── minecraft.service     # Systemd unit running the server
│   ├── minecraft-sync.service# Systemd oneshot unit syncing RAMDisk to disk
│   └── minecraft-sync.timer  # Systemd timer running sync every 5 minutes
└── tools/
    ├── noeddns/              # Cloudflare DDNS client in Rust (0 MB idle RAM, runs via timer)
    └── gpon-godmode/         # Port forwarding CLI for Nokia G-240W-F fiber ONT
```

---

## Infrastructure Tools

* **`tools/noeddns`** ([bsiamer/noeddns](https://github.com/bsiamer/noeddns)):
  Handles Dynamic DNS for Cloudflare. Runs via Linux `systemd.timer` once per minute, checks for public IP changes, updates the `A` record, and exits immediately. Uses 0 MB RAM when idle.

* **`tools/gpon-godmode`** ([bsiamer/gpon-godmode](https://github.com/bsiamer/gpon-godmode)):
  Automates opening port `25565` (TCP) on the Nokia G-240W-F fiber router to allow incoming player connections without using the router web UI.

---

## Server Mods (Fabric 26.3)

All mods are fetched directly from Modrinth CDN and GitHub releases using `./scripts/download_mods.sh`:

| Mod | Version | Purpose |
| :--- | :--- | :--- |
| **`fabric-api`** | `0.166.2+26.3` | Core API library for Fabric mods. |
| **`lithium`** | `0.26.4+mc26.3` | Optimizes physics, chunk ticking, and mob AI routines. |
| **`ferritecore`** | `9.0.0` | Compresses in-memory data structures to minimize heap footprint. |
| **`c2me`** | `0.4.2-alpha.0.121` | Parallelizes chunk generation and I/O across all 4 CPU cores. |
| **`krypton`** | `0.3.2` | Optimizes Netty networking pipeline and packet handling. |
| **`servercore`** | `1.5.21+26.3` | Dynamic tick rate optimizations for entities and view distances. |
| **`fabric-carpet`** | `26.3+v260915` | Server utilities and tick diagnostics. |
| **`fabrictailor`** | `2.11.0` | In-game skin support for `online-mode=false`. |
| **`simple-voice-chat`** | `2.6.27+26.3` | Proximity voice chat server backend (UDP 24454). |
| **`kamilsmcmod`** | `1.0.0` | Custom wandering trader assets. |

---

## Quick Setup & Deployment

### 1. Download Server Mods
```bash
./scripts/download_mods.sh /opt/minecraft/server/mods
```

### 2. Install Systemd Services
```bash
sudo cp systemd/minecraft.service /etc/systemd/system/
sudo cp systemd/minecraft-sync.service /etc/systemd/system/
sudo cp systemd/minecraft-sync.timer /etc/systemd/system/

sudo systemctl daemon-reload
sudo systemctl enable --now minecraft-sync.timer
sudo systemctl enable --now minecraft.service
```

---

## How to Join (For Friends)

Friends using **Pinecone** (or Prism Launcher) can import the complete modpack with one action:

1. Download [`test.mrpack`](test.mrpack) from this repository.
2. In Pinecone, click **Add Instance** -> **Import** (or drag and drop `test.mrpack` into the launcher).
3. Click **OK** to let Pinecone download all required mods (Fabulously Optimized baseline + `kamilsmcmod` + `Simple Voice Chat`).
4. Launch the game — **Joe The Duck** (`mc.joetheduck.lol`) is already pre-configured in the Multiplayer server list.
