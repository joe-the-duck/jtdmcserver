#!/bin/bash
set -e

DEST_DIR="${1:-mods}"
MODS_FILE="$(dirname "$0")/../mods.txt"

mkdir -p "$DEST_DIR"

echo "Downloading mods to '$DEST_DIR'..."

while IFS= read -r url || [ -n "$url" ]; do
    # Skip comments and empty lines
    [[ -z "$url" || "$url" =~ ^# ]] && continue

    filename=$(basename "$url" | sed 's/%2B/+/g')
    target="$DEST_DIR/$filename"

    if [ -f "$target" ]; then
        echo "  [EXISTS] $filename"
    else
        echo "  [FETCH]  $filename"
        curl -sSL -o "$target" "$url"
    fi
done < "$MODS_FILE"

echo "All mods ready in '$DEST_DIR'."
