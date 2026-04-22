#!/usr/bin/env python3
import os
import sys
import json
import requests
from pathlib import Path

CONFIG_FILE = Path(__file__).parent / "config.json"
API_BASE = "https://softhooky.com/api"
COST_GENERATE = 0.3
COST_EDIT = 0.3

def load_config():
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

def get_token():
    config = load_config()
    if not config.get("username") or not config.get("password"):
        print("ERROR: 请先配置账号密码")
        print("运行: python3 config.py set username <邮箱>")
        print("运行: python3 config.py set password <密码>")
        return None
    
    try:
        response = requests.post(
            f"{API_BASE}/auth/login",
            json={"email": config["username"], "password": config["password"]},
            timeout=30
        )
        data = response.json()
        if data.get("success"):
            config["token"] = data.get("token")
            config["credits"] = data.get("user", {}).get("credits", 0)
            save_config(config)
            return data.get("token")
        else:
            print(f"ERROR: 登录失败 - {data.get('message')}")
            return None
    except Exception as e:
        print(f"ERROR: 登录失败 - {str(e)}")
        return None

def get_credits(token):
    try:
        response = requests.get(
            f"{API_BASE}/auth/credits",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        data = response.json()
        return data.get("credits", 0)
    except Exception as e:
        print(f"ERROR: 获取积分失败 - {str(e)}")
        return 0

def generate_image(prompt, model="gemini-3.1-flash-image-preview", aspect_ratio="智能", resolution="1K"):
    token = get_token()
    if not token:
        return
    
    print(f"检查积分...")
    credits = get_credits(token)
    print(f"当前积分: {credits}")
    
    if credits < COST_GENERATE:
        print(f"ERROR: 积分不足，需要 {COST_GENERATE} 积分，当前仅有 {credits} 积分")
        return
    
    print(f"积分充足，开始生成图片...")
    print(f"Prompt: {prompt}")
    print(f"Model: {model}, Aspect: {aspect_ratio}, Resolution: {resolution}")
    
    try:
        response = requests.post(
            f"{API_BASE}/images/generations",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "prompt": prompt,
                "model": model,
                "aspectRatio": aspect_ratio,
                "resolution": resolution
            },
            timeout=300
        )
        
        if response.status_code == 400:
            error_data = response.json()
            if "积分" in error_data.get("error", ""):
                print(f"ERROR: {error_data.get('error')}")
                return
            raise Exception(error_data.get("error"))
        
        data = response.json()
        
        if data.get("data") and len(data["data"]) > 0:
            image_url = data["data"][0].get("url")
            remaining = data.get("remainingCredits", 0)
            print(f"SUCCESS: {image_url}")
            print(f"Remaining credits: {remaining}")
        else:
            print(f"ERROR: 生成失败 - {data}")
    except Exception as e:
        print(f"ERROR: 生成图片失败 - {str(e)}")

def edit_image(prompt, image_url, model="gemini-3.1-flash-image-preview"):
    token = get_token()
    if not token:
        return
    
    print(f"检查积分...")
    credits = get_credits(token)
    print(f"当前积分: {credits}")
    
    if credits < COST_EDIT:
        print(f"ERROR: 积分不足，需要 {COST_EDIT} 积分，当前仅有 {credits} 积分")
        return
    
    print(f"积分充足，开始编辑图片...")
    print(f"Prompt: {prompt}")
    print(f"Image: {image_url}")
    
    try:
        response = requests.post(
            f"{API_BASE}/images/edits",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json={
                "prompt": prompt,
                "images": [image_url],
                "model": model
            },
            timeout=300
        )
        
        if response.status_code == 400:
            error_data = response.json()
            if "积分" in error_data.get("error", ""):
                print(f"ERROR: {error_data.get('error')}")
                return
            raise Exception(error_data.get("error"))
        
        data = response.json()
        
        if data.get("data") and len(data["data"]) > 0:
            image_url = data["data"][0].get("url")
            remaining = data.get("remainingCredits", 0)
            print(f"SUCCESS: {image_url}")
            print(f"Remaining credits: {remaining}")
        else:
            print(f"ERROR: 编辑失败 - {data}")
    except Exception as e:
        print(f"ERROR: 编辑图片失败 - {str(e)}")

def show_credits():
    token = get_token()
    if not token:
        return
    
    credits = get_credits(token)
    print(f"当前积分: {credits}")

def main():
    if len(sys.argv) < 2:
        print("""
Softhooky 图片生成工具

用法:
    python3 softhooky.py generate <prompt> [model] [aspect_ratio] [resolution]
    python3 softhooky.py edit <prompt> <image_url> [model]
    python3 softhooky.py credits
    python3 softhooky.py config show
    python3 softhooky.py config set username <邮箱>
    python3 softhooky.py config set password <密码>

示例:
    python3 softhooky.py generate "一只可爱的猫咪" 
    python3 softhooky.py edit "添加装饰" "https://example.com/img.jpg"
    python3 softhooky.py credits
        """)
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "config":
        from config import main as config_main
        config_main()
    elif cmd == "generate":
        if len(sys.argv) < 3:
            print("ERROR: 请提供prompt")
            sys.exit(1)
        prompt = sys.argv[2]
        model = sys.argv[3] if len(sys.argv) > 3 else "gemini-3.1-flash-image-preview"
        aspect = sys.argv[4] if len(sys.argv) > 4 else "智能"
        resolution = sys.argv[5] if len(sys.argv) > 5 else "1K"
        generate_image(prompt, model, aspect, resolution)
    elif cmd == "edit":
        if len(sys.argv) < 4:
            print("ERROR: 请提供prompt和图片URL")
            sys.exit(1)
        prompt = sys.argv[2]
        image_url = sys.argv[3]
        model = sys.argv[4] if len(sys.argv) > 4 else "gemini-3.1-flash-image-preview"
        edit_image(prompt, image_url, model)
    elif cmd == "credits":
        show_credits()
    elif cmd == "login":
        token = get_token()
        if token:
            print("登录成功!")
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)

if __name__ == "__main__":
    main()