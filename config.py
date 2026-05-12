#!/usr/bin/env python3
import os
import json
import sys
from pathlib import Path

CONFIG_FILE = Path(__file__).parent / "config.json"

def load_config():
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

def get(key):
    config = load_config()
    return config.get(key)

def set_key(key, value):
    config = load_config()
    config[key] = value
    save_config(config)
    print(f"已设置 {key}: {value}")

def show():
    config = load_config()
    if config:
        for key, value in config.items():
            print(f"{key}: {value}")
    else:
        print("未配置任何信息")

def main():
    if len(sys.argv) < 2:
        print("Usage: config.py <command> [args]")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "get" and len(sys.argv) >= 3:
        value = get(sys.argv[2])
        print(value if value else "")
    elif cmd == "set" and len(sys.argv) >= 4:
        set_key(sys.argv[2], sys.argv[3])
    elif cmd == "show":
        show()
    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()