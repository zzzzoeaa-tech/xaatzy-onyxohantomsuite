#!/usr/bin/env python3
"""
TELEGRAM MASS REPORTER TOOL - FULL VERSION
Onyxphantom Suite - Coded By Xaatzy - Version 6.0.0
GitHub: https://github.com/onyxphantom/telegram-reporter
Contact: @craazin | t.me/craazin
"""

import os
import sys
import asyncio
import json
import re
import time
import base64
import hashlib
import platform
import subprocess
import socket
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

# ==================== CHECK & INSTALL MODULES ====================
def install_module(module):
    subprocess.check_call([sys.executable, "-m", "pip", "install", module])

try:
    from telethon import TelegramClient
    from telethon.errors import FloodWaitError, SessionPasswordNeededError
    from telethon.tl.functions.channels import JoinChannelRequest
    from telethon.tl.functions.messages import ReportSpamRequest
    from telethon.tl.types import (
        InputReportReasonChildAbuse,
        InputReportReasonViolence,
        InputReportReasonPornography,
        InputReportReasonOther,
        InputReportReasonSpam,
        InputReportReasonFake,
        InputReportReasonIllegalDrugs,
        InputReportReasonPersonalDetails
    )
except ImportError:
    print("[!] Installing telethon...")
    install_module("telethon")
    from telethon import TelegramClient
    from telethon.errors import FloodWaitError, SessionPasswordNeededError
    from telethon.tl.functions.channels import JoinChannelRequest
    from telethon.tl.functions.messages import ReportSpamRequest
    from telethon.tl.types import (
        InputReportReasonChildAbuse,
        InputReportReasonViolence,
        InputReportReasonPornography,
        InputReportReasonOther,
        InputReportReasonSpam,
        InputReportReasonFake,
        InputReportReasonIllegalDrugs,
        InputReportReasonPersonalDetails
    )

try:
    import aiohttp
except ImportError:
    print("[!] Installing aiohttp...")
    install_module("aiohttp")
    import aiohttp

try:
    import requests
except ImportError:
    print("[!] Installing requests...")
    install_module("requests")
    import requests

# ==================== KONFIGURASI ====================
GITHUB_CONFIG = {
    "owner": "zzzzoeaa-tech",
    "repo": "onyx-databases",
    "branch": "main",
    "token": "GITHUB_PERSONAL_ACCESS_TOKEN"
}
# Telegram API
API_ID = 25683949
API_HASH = "5a0f1b821252088fe36c523c01c82533"

# Bot Telegram untuk notifikasi
BOT_TOKEN = "8677431229:AAF7MxKXHesv0cSXfOU0K0Aw9tJCl65xNq8"
OWNER_CHAT_ID = "1394010666"

# Default Owner
DEFAULT_OWNER = {
    "username": "owner",
    "password": "admin123"
}

# ==================== WARNA ====================
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RESET = '\033[0m'

# ==================== ASCII ART ====================
ASCII_ART = f"""
{Colors.BLUE}   ___                         _                 _                  
{Colors.BLUE}  / _ \\ _ __  _   ___  ___ __ | |__   __ _ _ __ | |_ ___  _ __ ___  
{Colors.BLUE} | | | | '_ \\| | | \\ \\/ | '_ \\| '_ \\ / _` | '_ \\| __/ _ \\| '_ ` _ \\ 
{Colors.BLUE} | |_| | | | | |_| |>  <| |_) | | | | (_| | | | | || (_) | | | | | |
{Colors.BLUE}  \\___/|_| |_|\\__, /_/\\_| .__/|_| |_|\\__,_|_| |_|\\__\\___/|_| |_| |_|
{Colors.BLUE}            _ |___/     |_|                                         
{Colors.BLUE}  ___ _   _(_| |_ ___                                               
{Colors.BLUE} / __| | | | | __/ _ \\                                              
{Colors.BLUE} \\__ | |_| | | ||  __/                                              
{Colors.BLUE} |___/\\__,_|_|\\__\\___|                                              
{Colors.RESET}
{Colors.CYAN}{'═' * 60}{Colors.RESET}
{Colors.BOLD}{Colors.MAGENTA}               ONYXPHANTOM SUITE V8.4{Colors.RESET}
{Colors.CYAN}{'═' * 60}{Colors.RESET}
{Colors.DIM}                  Coded By Xaatzy{Colors.RESET}
{Colors.DIM}               Contact: @craazin{Colors.RESET}
{Colors.CYAN}{'═' * 60}{Colors.RESET}
"""

# ==================== GITHUB DATABASE ====================
class GitHubDatabase:
    def __init__(self):
        self.headers = {
            "Authorization": f"token {GITHUB_CONFIG['token']}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.base_url = f"https://api.github.com/repos/{GITHUB_CONFIG['owner']}/{GITHUB_CONFIG['repo']}/contents"
    
    async def read_file(self, path: str) -> Optional[dict]:
        url = f"{self.base_url}/{path}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as resp:
                if resp.status == 404:
                    return None
                if resp.status == 200:
                    data = await resp.json()
                    content = base64.b64decode(data["content"]).decode("utf-8")
                    return json.loads(content)
                return None
    
    async def write_file(self, path: str, data: dict, msg: str = "Update") -> bool:
        url = f"{self.base_url}/{path}"
        content = base64.b64encode(json.dumps(data, indent=2).encode()).decode()
        
        existing = None
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as resp:
                if resp.status == 200:
                    existing = await resp.json()
        
        payload = {"message": msg, "content": content, "branch": GITHUB_CONFIG["branch"]}
        if existing and "sha" in existing:
            payload["sha"] = existing["sha"]
        
        async with aiohttp.ClientSession() as session:
            async with session.put(url, headers=self.headers, json=payload) as resp:
                return resp.status == 201 or resp.status == 200

# ==================== BOT NOTIFIER ====================
class BotNotifier:
    def __init__(self):
        self.api_url = f"https://api.telegram.org/bot{BOT_TOKEN}"
    
    def get_public_ip(self):
        try:
            return requests.get('https://api.ipify.org', timeout=5).text
        except:
            return "Unknown"
    
    def send_notification(self, device_id: str, username: str, reason: str, block_type: str = "temporary"):
        public_ip = self.get_public_ip()
        hostname = platform.node()
        
        message = f"""
🚫 DEVICE BLOCKED NOTIFICATION

Device ID: {device_id[:16]}...
Username: {username}
Hostname: {hostname}
Public IP: {public_ip}
Reason: {reason}
Block Type: {block_type.upper()}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        try:
            requests.post(f"{self.api_url}/sendMessage", 
                         json={"chat_id": OWNER_CHAT_ID, "text": message})
        except:
            pass

# ==================== USER MANAGER ====================
class UserManager:
    def __init__(self, db: GitHubDatabase):
        self.db = db
    
    def hash_password(self, pwd: str) -> str:
        return hashlib.sha256(pwd.encode()).hexdigest()
    
    async def get_users(self) -> dict:
        data = await self.db.read_file("data/users.json")
        if not data:
            data = {
                "owner": DEFAULT_OWNER["username"],
                "users": {
                    DEFAULT_OWNER["username"]: {
                        "password": self.hash_password(DEFAULT_OWNER["password"]),
                        "created_at": datetime.now().isoformat(),
                        "role": "owner",
                        "banned": False,
                        "sessions": [],
                        "stats": {"total": 0, "success": 0, "failed": 0}
                    }
                }
            }
            await self.db.write_file("data/users.json", data, "Init users")
            print(f"\n{Colors.GREEN}[✓] Default owner created: owner / admin123{Colors.RESET}")
        return data
    
    async def verify_user(self, username: str, password: str, device_id: str) -> Tuple[bool, dict]:
        data = await self.get_users()
        if username not in data["users"]:
            return False, {"error": "User not found"}
        
        user = data["users"][username]
        if user["password"] != self.hash_password(password):
            return False, {"error": "Wrong password"}
        if user.get("banned", False):
            return False, {"error": "User is banned"}
        if user.get("role") != "owner" and user.get("expiry"):
            if datetime.now() > datetime.fromisoformat(user["expiry"]):
                return False, {"error": "License expired"}
        
        user["last_login"] = datetime.now().isoformat()
        user["last_device"] = device_id
        await self.db.write_file("data/users.json", data, f"Login: {username}")
        return True, user
    
    async def add_user(self, owner: str, username: str, password: str, days: int = 30) -> bool:
        data = await self.get_users()
        if data.get("owner") != owner:
            return False
        if username in data["users"]:
            return False
        
        expiry = (datetime.now() + timedelta(days=days)).isoformat()
        data["users"][username] = {
            "password": self.hash_password(password),
            "created_at": datetime.now().isoformat(),
            "expiry": expiry,
            "role": "user",
            "banned": False,
            "sessions": [],
            "stats": {"total": 0, "success": 0, "failed": 0}
        }
        return await self.db.write_file("data/users.json", data, f"Add user: {username}")
    
    async def remove_user(self, owner: str, username: str) -> bool:
        data = await self.get_users()
        if data.get("owner") != owner or username == data.get("owner"):
            return False
        if username in data["users"]:
            del data["users"][username]
            return await self.db.write_file("data/users.json", data, f"Remove user: {username}")
        return False
    
    async def ban_user(self, owner: str, username: str) -> bool:
        data = await self.get_users()
        if data.get("owner") != owner:
            return False
        if username in data["users"] and data["users"][username].get("role") != "owner":
            data["users"][username]["banned"] = True
            return await self.db.write_file("data/users.json", data, f"Ban user: {username}")
        return False
    
    async def unban_user(self, owner: str, username: str) -> bool:
        data = await self.get_users()
        if data.get("owner") != owner:
            return False
        if username in data["users"]:
            data["users"][username]["banned"] = False
            return await self.db.write_file("data/users.json", data, f"Unban user: {username}")
        return False
    
    async def extend_user(self, owner: str, username: str, days: int) -> bool:
        data = await self.get_users()
        if data.get("owner") != owner:
            return False
        if username in data["users"] and data["users"][username].get("role") != "owner":
            new_expiry = datetime.fromisoformat(data["users"][username]["expiry"]) + timedelta(days=days)
            data["users"][username]["expiry"] = new_expiry.isoformat()
            return await self.db.write_file("data/users.json", data, f"Extend user: {username}")
        return False
    
    async def list_users(self, owner: str) -> List[dict]:
        data = await self.get_users()
        if data.get("owner") != owner:
            return []
        return [{"username": u, **v} for u, v in data["users"].items()]

# ==================== DEVICE MANAGER ====================
class DeviceManager:
    def __init__(self, db: GitHubDatabase):
        self.db = db
        self.bot = BotNotifier()
    
    async def get_devices(self) -> dict:
        data = await self.db.read_file("data/devices.json")
        if not data:
            data = {"devices": {}, "blocked_devices": []}
            await self.db.write_file("data/devices.json", data, "Init devices")
        return data
    
    async def register_device(self, username: str, device_id: str) -> bool:
        data = await self.get_devices()
        if device_id not in data["devices"]:
            data["devices"][device_id] = {
                "owner": username,
                "name": f"{platform.system()} - {platform.node()}",
                "first_seen": datetime.now().isoformat(),
                "last_seen": datetime.now().isoformat(),
                "failed_attempts": 0,
                "blocked": False
            }
        else:
            data["devices"][device_id]["last_seen"] = datetime.now().isoformat()
        return await self.db.write_file("data/devices.json", data, f"Register device")
    
    async def is_blocked(self, device_id: str) -> Tuple[bool, str]:
        data = await self.get_devices()
        if device_id in data.get("blocked_devices", []):
            return True, "Device permanently blocked"
        if device_id in data["devices"] and data["devices"][device_id].get("blocked"):
            return True, "Device blocked by owner"
        return False, ""
    
    async def record_failed(self, device_id: str, username: str = None) -> Tuple[bool, str]:
        data = await self.get_devices()
        if device_id not in data["devices"]:
            data["devices"][device_id] = {
                "owner": username or "unknown",
                "name": f"{platform.system()} - {platform.node()}",
                "first_seen": datetime.now().isoformat(),
                "last_seen": datetime.now().isoformat(),
                "failed_attempts": 0,
                "blocked": False
            }
        
        device = data["devices"][device_id]
        device["failed_attempts"] = device.get("failed_attempts", 0) + 1
        
        if device["failed_attempts"] >= 3:
            device["blocked"] = True
            data["blocked_devices"].append(device_id)
            await self.db.write_file("data/devices.json", data, f"Block device")
            self.bot.send_notification(device_id, username or "unknown", "3 failed attempts", "temporary")
            return True, "Device blocked after 3 failed attempts"
        
        await self.db.write_file("data/devices.json", data, f"Failed attempt")
        return False, f"{3 - device['failed_attempts']} attempts left"
    
    async def reset_attempts(self, device_id: str) -> bool:
        data = await self.get_devices()
        if device_id in data["devices"]:
            data["devices"][device_id]["failed_attempts"] = 0
            return await self.db.write_file("data/devices.json", data, "Reset attempts")
        return False

# ==================== SESSION MANAGER ====================
class SessionManager:
    def __init__(self, db: GitHubDatabase, username: str):
        self.db = db
        self.username = username
        self.sessions = []
        self.local_dir = f"sessions_{username}"
        self.stats = {"total": 0, "success": 0, "failed": 0}
    
    async def load(self):
        users = await self.db.read_file("data/users.json")
        if users and self.username in users["users"]:
            self.sessions = users["users"][self.username].get("sessions", [])
            self.stats = users["users"][self.username].get("stats", {"total": 0, "success": 0, "failed": 0})
        
        if not os.path.exists(self.local_dir):
            os.makedirs(self.local_dir)
        
        for s in self.sessions:
            local_file = os.path.join(self.local_dir, s["file"])
            if not os.path.exists(local_file):
                session_data = await self.db.read_file(f"sessions/{self.username}/{s['file']}")
                if session_data and "content" in session_data:
                    with open(local_file, "wb") as f:
                        f.write(base64.b64decode(session_data["content"]))
        return len(self.sessions)
    
    async def save(self):
        users = await self.db.read_file("data/users.json")
        if users and self.username in users["users"]:
            users["users"][self.username]["sessions"] = self.sessions
            users["users"][self.username]["stats"] = self.stats
            await self.db.write_file("data/users.json", users, f"Update {self.username}")
    
    async def add_session(self, phone: str, user_id: int, name: str, data: bytes):
        session_file = f"{user_id}.session"
        local_path = os.path.join(self.local_dir, session_file)
        with open(local_path, "wb") as f:
            f.write(data)
        
        await self.db.write_file(f"sessions/{self.username}/{session_file}", 
                                {"content": base64.b64encode(data).decode()}, "Add session")
        
        self.sessions.append({
            "id": user_id, "phone": phone, "file": session_file, "name": name,
            "added_at": datetime.now().isoformat()
        })
        await self.save()
        return True
    
    async def remove_session(self, index: int):
        if 0 <= index < len(self.sessions):
            session = self.sessions.pop(index)
            local_path = os.path.join(self.local_dir, session["file"])
            if os.path.exists(local_path):
                os.remove(local_path)
            await self.save()
            return True
        return False
    
    async def get_clients(self):
        clients = []
        for s in self.sessions:
            try:
                session_file = os.path.join(self.local_dir, s["file"])
                if os.path.exists(session_file):
                    client = TelegramClient(session_file, API_ID, API_HASH)
                    await client.connect()
                    if await client.is_user_authorized():
                        clients.append((s["id"], client))
                    else:
                        await client.disconnect()
            except:
                pass
        return clients

# ==================== TELEGRAM REPORTER ====================
class TelegramReporter:
    def __init__(self, sm: SessionManager):
        self.sm = sm
        self.settings = {"delay": 3}
    
    def extract_username(self, text):
        text = text.strip()
        if text.startswith("@"):
            text = text[1:]
        if "t.me/" in text:
            parts = text.split("t.me/")
            if len(parts) > 1:
                text = parts[1].split("/")[0]
        return re.sub(r"[^a-zA-Z0-9_]", "", text) if len(text) > 2 else None
    
    async def report_channel(self, target: str, count: int = 1):
        username = self.extract_username(target)
        if not username:
            print(f"{Colors.RED}[!] Invalid target{Colors.RESET}")
            return False
        
        clients = await self.sm.get_clients()
        if not clients:
            print(f"{Colors.RED}[!] No active sessions{Colors.RESET}")
            return False
        
        total = 0
        for uid, client in clients:
            try:
                entity = await client.get_entity(username)
                for i in range(count):
                    try:
                        await client(ReportSpamRequest(peer=entity))
                        total += 1
                        self.sm.stats["total"] += 1
                        self.sm.stats["success"] += 1
                        print(f"{Colors.CYAN}⣾ Reported {i+1}/{count} from session {uid}{Colors.RESET}", end="\r")
                    except FloodWaitError as e:
                        print(f"\n{Colors.YELLOW}[!] Flood wait {e.seconds}s{Colors.RESET}")
                        await asyncio.sleep(e.seconds)
                    except Exception as e:
                        print(f"\n{Colors.RED}[!] Failed: {e}{Colors.RESET}")
                        self.sm.stats["total"] += 1
                        self.sm.stats["failed"] += 1
                    await asyncio.sleep(self.settings["delay"])
                await client.disconnect()
            except:
                pass
        
        print()
        await self.sm.save()
        print(f"{Colors.GREEN}[✓] Total reports: {total}{Colors.RESET}")
        return total > 0
    
    async def login_telegram(self):
        print(f"\n{Colors.CYAN}▢ TELEGRAM LOGIN{Colors.RESET}")
        phone = input(f"{Colors.GREEN}Phone (+62xxx): {Colors.RESET}").strip()
        if not phone.startswith("+"):
            phone = "+" + phone
        
        for s in self.sm.sessions:
            if s.get("phone") == phone:
                print(f"{Colors.YELLOW}[!] Session exists{Colors.RESET}")
                input("Press Enter...")
                return
        
        session_file = os.path.join(self.sm.local_dir, f"temp_{int(time.time())}.session")
        
        try:
            client = TelegramClient(session_file, API_ID, API_HASH)
            await client.connect()
            
            if not await client.is_user_authorized():
                await client.send_code_request(phone)
                code = input(f"{Colors.GREEN}Code: {Colors.RESET}")
                try:
                    await client.sign_in(phone, code)
                except:
                    pwd = input(f"{Colors.GREEN}2FA Password: {Colors.RESET}")
                    await client.sign_in(password=pwd)
            
            me = await client.get_me()
            with open(session_file, "rb") as f:
                content = f.read()
            
            await self.sm.add_session(phone, me.id, me.first_name or "", content)
            os.remove(session_file)
            print(f"{Colors.GREEN}[✓] Login successful!{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.RED}[!] Failed: {e}{Colors.RESET}")
            if os.path.exists(session_file):
                os.remove(session_file)
        input("Press Enter...")

# ==================== OWNER PANEL ====================
class OwnerPanel:
    def __init__(self, um: UserManager, dm: DeviceManager, username: str):
        self.um = um
        self.dm = dm
        self.username = username
    
    async def show(self):
        while True:
            os.system("clear" if os.name == "posix" else "cls")
            print(ASCII_ART)
            print(f"""
{Colors.CYAN}{'═' * 60}{Colors.RESET}
{Colors.BOLD}{Colors.RED}👑 OWNER PANEL{Colors.RESET}
{Colors.CYAN}{'═' * 60}{Colors.RESET}

{Colors.GREEN}[1]{Colors.RESET} Add User
{Colors.GREEN}[2]{Colors.RESET} Remove User
{Colors.GREEN}[3]{Colors.RESET} Ban/Unban User
{Colors.GREEN}[4]{Colors.RESET} Extend License
{Colors.GREEN}[5]{Colors.RESET} List Users
{Colors.GREEN}[6]{Colors.RESET} Block Device
{Colors.GREEN}[7]{Colors.RESET} Unblock Device
{Colors.GREEN}[8]{Colors.RESET} List Devices
{Colors.GREEN}[0]{Colors.RESET} Back

{Colors.CYAN}{'═' * 60}{Colors.RESET}
            """)
            choice = input(f"{Colors.GREEN}Choice: {Colors.RESET}")
            
            if choice == "1":
                u = input("Username: ")
                p = input("Password: ")
                d = int(input("Days: ") or "30")
                if await self.um.add_user(self.username, u, p, d):
                    print(f"{Colors.GREEN}[✓] User {u} added{Colors.RESET}")
                else:
                    print(f"{Colors.RED}[!] Failed{Colors.RESET}")
                input("Press Enter...")
            elif choice == "2":
                u = input("Username: ")
                if await self.um.remove_user(self.username, u):
                    print(f"{Colors.GREEN}[✓] User {u} removed{Colors.RESET}")
                else:
                    print(f"{Colors.RED}[!] Failed{Colors.RESET}")
                input("Press Enter...")
            elif choice == "3":
                u = input("Username: ")
                a = input("Ban (b) or Unban (u): ").lower()
                if a == "b":
                    if await self.um.ban_user(self.username, u):
                        print(f"{Colors.GREEN}[✓] User {u} banned{Colors.RESET}")
                elif a == "u":
                    if await self.um.unban_user(self.username, u):
                        print(f"{Colors.GREEN}[✓] User {u} unbanned{Colors.RESET}")
                input("Press Enter...")
            elif choice == "4":
                u = input("Username: ")
                d = int(input("Extra days: "))
                if await self.um.extend_user(self.username, u, d):
                    print(f"{Colors.GREEN}[✓] User {u} extended{Colors.RESET}")
                input("Press Enter...")
            elif choice == "5":
                users = await self.um.list_users(self.username)
                print(f"\n{Colors.CYAN}{'═' * 60}{Colors.RESET}")
                for u in users:
                    status = f"{Colors.RED}BANNED{Colors.RESET}" if u.get("banned") else f"{Colors.GREEN}ACTIVE{Colors.RESET}"
                    role = f"{Colors.YELLOW}[{u['role'].upper()}]{Colors.RESET}" if u['role'] == 'owner' else ""
                    print(f"{Colors.GREEN}{u['username']}{Colors.RESET}: {status} {role}")
                    print(f"  Expiry: {u.get('expiry', 'Never')[:10]}")
                    print(f"  Sessions: {len(u.get('sessions', []))}")
                    print()
                input("Press Enter...")
            elif choice == "6":
                devices = await self.dm.get_devices()
                print(f"\n{Colors.CYAN}{'═' * 60}{Colors.RESET}")
                for i, (did, info) in enumerate(devices["devices"].items(), 1):
                    print(f"{i}. {info['name']} - {did[:16]}...")
                    print(f"   Owner: {info['owner']}")
                try:
                    idx = int(input("Select device: "))
                    did = list(devices["devices"].keys())[idx-1]
                    devices["devices"][did]["blocked"] = True
                    devices["blocked_devices"].append(did)
                    await self.dm.db.write_file("data/devices.json", devices, "Block device")
                    print(f"{Colors.GREEN}[✓] Device blocked{Colors.RESET}")
                except:
                    pass
                input("Press Enter...")
            elif choice == "7":
                devices = await self.dm.get_devices()
                blocked = [d for d in devices["blocked_devices"]]
                for i, did in enumerate(blocked, 1):
                    print(f"{i}. {did[:16]}...")
                try:
                    idx = int(input("Select device: "))
                    did = blocked[idx-1]
                    devices["blocked_devices"].remove(did)
                    if did in devices["devices"]:
                        devices["devices"][did]["blocked"] = False
                    await self.dm.db.write_file("data/devices.json", devices, "Unblock device")
                    print(f"{Colors.GREEN}[✓] Device unblocked{Colors.RESET}")
                except:
                    pass
                input("Press Enter...")
            elif choice == "8":
                devices = await self.dm.get_devices()
                print(f"\n{Colors.CYAN}{'═' * 60}{Colors.RESET}")
                for did, info in devices["devices"].items():
                    status = f"{Colors.RED}BLOCKED{Colors.RESET}" if info.get("blocked") else f"{Colors.GREEN}ACTIVE{Colors.RESET}"
                    print(f"{Colors.CYAN}Device:{Colors.RESET} {info['name']} [{status}]")
                    print(f"  ID: {did}")
                    print(f"  Owner: {info['owner']}")
                    print(f"  Failed: {info.get('failed_attempts', 0)}")
                    print()
                input("Press Enter...")
            elif choice == "0":
                break

# ==================== MAIN MENU ====================
class MainMenu:
    def __init__(self, username: str, role: str, device_id: str):
        self.username = username
        self.role = role
        self.device_id = device_id
        self.db = GitHubDatabase()
        self.um = UserManager(self.db)
        self.dm = DeviceManager(self.db)
        self.sm = SessionManager(self.db, username)
        self.reporter = None
    
    async def run(self):
        await self.dm.register_device(self.username, self.device_id)
        await self.sm.load()
        self.reporter = TelegramReporter(self.sm)
        
        while True:
            os.system("clear" if os.name == "posix" else "cls")
            print(ASCII_ART)
            
            rate = (self.sm.stats["success"] / self.sm.stats["total"] * 100) if self.sm.stats["total"] > 0 else 0
            
            owner_menu = f"\n{Colors.GREEN}[A]{Colors.RESET} ▢ Owner Panel 👑" if self.role == "owner" else ""
            
            print(f"""
{Colors.CYAN}{'═' * 60}{Colors.RESET}
{Colors.BOLD}{Colors.YELLOW}▢ MAIN MENU{Colors.RESET}
{Colors.CYAN}{'═' * 60}{Colors.RESET}

{Colors.GREEN}[1]{Colors.RESET} ▢ Login Telegram
{Colors.GREEN}[2]{Colors.RESET} ▢ Report Channel/Group
{Colors.GREEN}[3]{Colors.RESET} ▢ Report Post
{Colors.GREEN}[4]{Colors.RESET} ▢ Report Account
{Colors.GREEN}[5]{Colors.RESET} ▢ Report Bot
{Colors.GREEN}[6]{Colors.RESET} ▢ Statistics
{Colors.GREEN}[7]{Colors.RESET} ▢ List Sessions
{Colors.GREEN}[8]{Colors.RESET} ▢ Remove Session
{Colors.GREEN}[9]{Colors.RESET} ▢ Settings
{owner_menu}
{Colors.GREEN}[0]{Colors.RESET} ▢ Logout

{Colors.CYAN}{'═' * 60}{Colors.RESET}
{Colors.DIM}User: {self.username} ({self.role}) | Sessions: {len(self.sm.sessions)} | Reports: {self.sm.stats['total']} | Rate: {rate:.0f}%{Colors.RESET}
{Colors.CYAN}{'═' * 60}{Colors.RESET}
            """)
            
            choice = input(f"{Colors.GREEN}Choice: {Colors.RESET}").lower()
            
            if choice == "1":
                await self.reporter.login_telegram()
            elif choice == "2":
                target = input(f"{Colors.GREEN}Target: {Colors.RESET}")
                cnt = int(input(f"{Colors.GREEN}Count (1-100): {Colors.RESET}") or "1")
                await self.reporter.report_channel(target, min(cnt, 100))
                input("Press Enter...")
            elif choice == "3":
                target = input(f"{Colors.GREEN}Post link: {Colors.RESET}")
                cnt = int(input(f"{Colors.GREEN}Count (1-100): {Colors.RESET}") or "1")
                channel = re.search(r"t\.me/([a-zA-Z0-9_]+)", target)
                if channel:
                    await self.reporter.report_channel(channel.group(1), min(cnt, 100))
                input("Press Enter...")
            elif choice == "4":
                target = input(f"{Colors.GREEN}Username: {Colors.RESET}")
                cnt = int(input(f"{Colors.GREEN}Count (1-100): {Colors.RESET}") or "1")
                await self.reporter.report_channel(target, min(cnt, 100))
                input("Press Enter...")
            elif choice == "5":
                target = input(f"{Colors.GREEN}Bot username: {Colors.RESET}")
                cnt = int(input(f"{Colors.GREEN}Count (1-100): {Colors.RESET}") or "1")
                await self.reporter.report_channel(target, min(cnt, 100))
                input("Press Enter...")
            elif choice == "6":
                print(f"""
{Colors.CYAN}{'═' * 60}{Colors.RESET}
{Colors.BOLD}{Colors.YELLOW}▢ STATISTICS{Colors.RESET}
{Colors.CYAN}{'═' * 60}{Colors.RESET}

{Colors.GREEN}Total Reports:{Colors.RESET} {self.sm.stats['total']}
{Colors.GREEN}Success:{Colors.RESET} {self.sm.stats['success']}
{Colors.GREEN}Failed:{Colors.RESET} {self.sm.stats['failed']}
{Colors.GREEN}Rate:{Colors.RESET} {rate:.0f}%
{Colors.CYAN}{'═' * 60}{Colors.RESET}
                """)
                input("Press Enter...")
            elif choice == "7":
                for i, s in enumerate(self.sm.sessions, 1):
                    print(f"{i}. {s.get('phone', '?')[-8:]} | {s.get('name', '?')[:15]}")
                input("Press Enter...")
            elif choice == "8":
                for i, s in enumerate(self.sm.sessions, 1):
                    print(f"{i}. {s.get('phone', '?')[-8:]}")
                try:
                    idx = int(input("Select: ")) - 1
                    await self.sm.remove_session(idx)
                    print(f"{Colors.GREEN}[✓] Removed{Colors.RESET}")
                except:
                    pass
                input("Press Enter...")
            elif choice == "9":
                new_delay = int(input(f"Delay ({self.reporter.settings['delay']}s): ") or "3")
                self.reporter.settings["delay"] = max(1, min(10, new_delay))
                print(f"{Colors.GREEN}[✓] Delay set to {self.reporter.settings['delay']}s{Colors.RESET}")
                input("Press Enter...")
            elif choice == "a" and self.role == "owner":
                owner = OwnerPanel(self.um, self.dm, self.username)
                await owner.show()
            elif choice == "0":
                print(f"\n{Colors.GREEN}Goodbye!{Colors.RESET}")
                break

# ==================== LOGIN ====================
def get_device_id() -> str:
    system = platform.system()
    if system == "Linux":
        try:
            with open('/etc/machine-id', 'r') as f:
                return hashlib.sha256(f.read().strip().encode()).hexdigest()[:32]
        except:
            pass
    hostname = platform.node()
    username = os.getlogin() if hasattr(os, 'getlogin') else 'unknown'
    return hashlib.sha256(f"{hostname}_{username}".encode()).hexdigest()[:32]

async def login_screen():
    db = GitHubDatabase()
    um = UserManager(db)
    dm = DeviceManager(db)
    device_id = get_device_id()
    
    attempts = 0
    while attempts < 3:
        os.system("clear" if os.name == "posix" else "cls")
        print(ASCII_ART)
        print(f"\n{Colors.CYAN}▢ LOGIN{Colors.RESET}\n")
        
        # Check if device blocked
        blocked, msg = await dm.is_blocked(device_id)
        if blocked:
            print(f"{Colors.RED}⚠️ {msg}{Colors.RESET}")
            input("\nPress Enter...")
            return None, None, None
        
        username = input(f"{Colors.GREEN}Username: {Colors.RESET}")
        password = input(f"{Colors.GREEN}Password: {Colors.RESET}")
        
        verified, user_data = await um.verify_user(username, password, device_id)
        
        if verified:
            await dm.reset_attempts(device_id)
            print(f"\n{Colors.GREEN}✅ Welcome back, {username}!{Colors.RESET}")
            await asyncio.sleep(1)
            return username, user_data.get("role", "user"), device_id
        else:
            attempts += 1
            blocked, msg = await dm.record_failed(device_id, username)
            print(f"\n{Colors.RED}❌ {user_data.get('error', 'Login failed')}{Colors.RESET}")
            if blocked:
                print(f"{Colors.RED}⚠️ {msg}{Colors.RESET}")
                input("\nPress Enter...")
                return None, None, None
            print(f"{Colors.YELLOW}⚠️ {3 - attempts} attempts left{Colors.RESET}")
            await asyncio.sleep(1)
    
    print(f"\n{Colors.RED}🔒 Device blocked!{Colors.RESET}")
    input("\nPress Enter...")
    return None, None, None

# ==================== MAIN ====================
async def main():
    try:
        username, role, device_id = await login_screen()
        if username:
            menu = MainMenu(username, role, device_id)
            await menu.run()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️ Stopped{Colors.RESET}")
    except Exception as e:
        print(f"\n{Colors.RED}❌ Error: {e}{Colors.RESET}")

if __name__ == "__main__":
    asyncio.run(main())
