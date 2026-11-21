#!/bin/bash
set -e

SERVER_DIR="${SERVER_DIR:-/opt/minecraft/server}"
SCRIPTS_DIR="${SCRIPTS_DIR:-/opt/minecraft/scripts}"

cd "$SERVER_DIR"

# Ensure RAMDisk is mounted and loaded
"$SCRIPTS_DIR/sync_world.sh" init

# Trap exit to ensure world is cleanly saved to persistent storage on shutdown
cleanup() {
    echo "[Server] Saving world to disk..."
    "$SCRIPTS_DIR/sync_world.sh" save
}
trap cleanup EXIT

# Start Fabric server with 4-core parallel GC & memory optimization
exec java \
  -Xms3G -Xmx3G \
  -XX:+UseG1GC \
  -XX:ParallelGCThreads=4 \
  -XX:ConcGCThreads=2 \
  -XX:+UnlockExperimentalVMOptions \
  -XX:+AlwaysPreTouch \
  -XX:G1NewSizePercent=30 \
  -XX:G1MaxNewSizePercent=40 \
  -XX:G1ReservePercent=15 \
  -XX:InitiatingHeapOccupancyPercent=15 \
  -XX:G1MixedGCLiveThresholdPercent=90 \
  -XX:G1RSetUpdatingPauseTimePercent=5 \
  -XX:SurvivorRatio=32 \
  -XX:+PerfDisableSharedMem \
  -XX:MaxTenuringThreshold=1 \
  -Dfabric.development=false \
  -jar fabric-server-launch.jar nogui
