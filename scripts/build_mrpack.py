#!/usr/bin/env python3
import os
import json
import zipfile
import hashlib
import tempfile
import shutil

def build_servers_dat(name, ip):
    b_name = name.encode("utf-8")
    b_ip = ip.encode("utf-8")
    
    nbt = bytearray()
    nbt += b"\x0a\x00\x00"                  # TAG_Compound("")
    nbt += b"\x09\x00\x07servers"          # TAG_List("servers")
    nbt += b"\x0a"                         # list element type: TAG_Compound
    nbt += (1).to_bytes(4, "big")          # list length: 1
    
    # element 0 compound
    nbt += b"\x08\x00\x04name" + len(b_name).to_bytes(2, "big") + b_name
    nbt += b"\x08\x00\x02ip" + len(b_ip).to_bytes(2, "big") + b_ip
    nbt += b"\x01\x00\x06hidden\x00"       # TAG_Byte("hidden", 0)
    nbt += b"\x00"                         # end of element compound
    nbt += b"\x00"                         # end of root compound
    return bytes(nbt)

def main():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_mrpack = os.path.join(repo_root, "test.mrpack")
    
    base_index_path = "/home/noe/.local/share/ElyPrismLauncher/instances/test/mrpack/modrinth.index.json"
    with open(base_index_path, "r", encoding="utf-8") as f:
        index = json.load(f)

    # 1. Update metadata and pay tribute to Fabulously Optimized
    index["name"] = "test"
    index["versionId"] = "1.0.0"
    index["summary"] = (
        "Client modpack for Joe The Duck server (mc.joetheduck.lol). "
        "Built on top of Fabulously Optimized by RobotPantheon and contributors (fabulously-optimized.com)."
    )

    # 2. Add extra mods (skinshuffle, waveycapes, simple-voice-chat) with exact verified hashes
    extra_mods = [
        {
            "path": "mods/skinshuffle-2.14.0+26.3-fabric.jar",
            "hashes": {
                "sha1": "e25c348f9c313bb74a00844d6ee4f07f41d54087",
                "sha512": "1c5c7a2ca8124d2f4b121b04c2b0e8fe3f76994c80b840c26457a0e23cf83ab723e72a4c400f1b49a0b391f256755caaca8d3e436d62ae54d45acbdef899fed9"
            },
            "env": {
                "client": "required",
                "server": "unsupported"
            },
            "downloads": [
                "https://cdn.modrinth.com/data/3s19I5jr/versions/R2FqiNx5/skinshuffle-2.14.0%2B26.3-fabric.jar"
            ],
            "fileSize": 5301897
        },
        {
            "path": "mods/waveycapes-fabric-1.11.3-mc26.3.jar",
            "hashes": {
                "sha1": "abf486eb5e338c6da17add315afa9fae38afbed8",
                "sha512": "8be4bbe1efdf9ccb0d57b4e399849c52ac9034b3ba12012cb71e4951a800205b81bb4e035b7558c2005cce43acf7840b8ef0ca9f3568a22a7633dbf398866a21"
            },
            "env": {
                "client": "required",
                "server": "unsupported"
            },
            "downloads": [
                "https://cdn.modrinth.com/data/kYuIpRLv/versions/HzJI5xeL/waveycapes-fabric-1.11.3-mc26.3.jar"
            ],
            "fileSize": 1764922
        },
        {
            "path": "mods/voicechat-fabric-2.6.27+26.3.jar",
            "hashes": {
                "sha1": "23442735927fe3839650196c0656eb82b0322d87",
                "sha512": "f2de66761c0f249bb0f9a4b348f98b97ab4e89d3ed3fd37638420364b7431b757933aa08c0cc3e7ba3dd85a602d6c2de313c2309fc587e93cabf31fc5f6df27e"
            },
            "env": {
                "client": "required",
                "server": "required"
            },
            "downloads": [
                "https://cdn.modrinth.com/data/9eGKb6K1/versions/x9jLR94Q/voicechat-fabric-2.6.27%2B26.3.jar"
            ],
            "fileSize": 1419468
        }
    ]

    # Deduplicate by path
    existing_paths = {f["path"] for f in index["files"]}
    for m in extra_mods:
        if m["path"] not in existing_paths:
            index["files"].append(m)

    # 3. Create zip
    with tempfile.TemporaryDirectory() as tmpdir:
        # Write modrinth.index.json
        index_file = os.path.join(tmpdir, "modrinth.index.json")
        with open(index_file, "w", encoding="utf-8") as f:
            json.dump(index, f, indent=2)

        # Overrides: pre-configured servers.dat and kamilsmcmod bundled directly
        overrides_dir = os.path.join(tmpdir, "overrides")
        os.makedirs(os.path.join(overrides_dir, "mods"), exist_ok=True)
        
        # 1. Servers list
        servers_dat = build_servers_dat("Joe The Duck", "mc.joetheduck.lol")
        with open(os.path.join(overrides_dir, "servers.dat"), "wb") as f:
            f.write(servers_dat)

        # 2. Bundle local mods directly into overrides/mods so they require 0 network requests
        kamil_src = "/home/noe/.local/share/ElyPrismLauncher/instances/test/minecraft/mods/kamilsmcmod-1.0.0.jar"
        if os.path.exists(kamil_src):
            shutil.copy2(kamil_src, os.path.join(overrides_dir, "mods", "kamilsmcmod-1.0.0.jar"))

        bfdi_src = "/home/noe/Projects/funny-bfdi/build/libs/funnybfdi-1.2.0.jar"
        if os.path.exists(bfdi_src):
            shutil.copy2(bfdi_src, os.path.join(overrides_dir, "mods", "funnybfdi-1.2.0.jar"))

        # Copy FO config defaults if present
        fo_defaults = "/home/noe/.local/share/ElyPrismLauncher/instances/test/minecraft/config/modpack_defaults"
        if os.path.isdir(fo_defaults):
            dst = os.path.join(overrides_dir, "config", "modpack_defaults")
            shutil.copytree(fo_defaults, dst, dirs_exist_ok=True)

        # Build zip with safe timestamps
        print(f"Creating {output_mrpack}...")
        with zipfile.ZipFile(output_mrpack, "w", compression=zipfile.ZIP_DEFLATED, strict_timestamps=False) as zf:
            for root, _, files in os.walk(tmpdir):
                for file in files:
                    full_p = os.path.join(root, file)
                    rel_p = os.path.relpath(full_p, tmpdir)
                    zinfo = zipfile.ZipInfo(rel_p, date_time=(2026, 1, 1, 0, 0, 0))
                    with open(full_p, "rb") as f_in:
                        zf.writestr(zinfo, f_in.read())

    print(f"Successfully generated {output_mrpack} with {len(index['files'])} mods.")

if __name__ == "__main__":
    main()
