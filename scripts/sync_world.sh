#!/bin/bash
set -e

ACTION=$1
WORLD_RAM="/opt/minecraft/server/world"
WORLD_DISK="/opt/minecraft/persistent_world"

case "$ACTION" in
    init)
        mkdir -p "$WORLD_RAM" "$WORLD_DISK"
        if ! mountpoint -q "$WORLD_RAM"; then
            echo "[RAMDisk] Mounting 2G tmpfs on $WORLD_RAM"
            mount -t tmpfs -o size=2G,noatime,nodiratime tmpfs "$WORLD_RAM"
        fi
        if [ -d "$WORLD_DISK" ] && [ "$(ls -A "$WORLD_DISK" 2>/dev/null)" ]; then
            echo "[RAMDisk] Loading world from disk to RAM..."
            rsync -a "$WORLD_DISK/" "$WORLD_RAM/"
        else
            echo "[RAMDisk] Fresh world initialized in RAM."
        fi
        ;;
    save)
        if mountpoint -q "$WORLD_RAM" && [ "$(ls -A "$WORLD_RAM" 2>/dev/null)" ]; then
            rsync -a --delete "$WORLD_RAM/" "$WORLD_DISK/"
            echo "[RAMDisk] Synced RAM world to disk at $(date)"
        fi
        ;;
    shutdown)
        if mountpoint -q "$WORLD_RAM"; then
            echo "[RAMDisk] Final sync before unmount..."
            rsync -a --delete "$WORLD_RAM/" "$WORLD_DISK/"
            umount "$WORLD_RAM"
            echo "[RAMDisk] Successfully unmounted RAM world."
        fi
        ;;
    *)
        echo "Usage: $0 {init|save|shutdown}"
        exit 1
        ;;
esac
