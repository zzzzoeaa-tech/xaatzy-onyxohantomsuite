#!/usr/bin/env python3
"""
TELEGRAM MASS REPORTER TOOL - SHARED SESSIONS VERSION
Onyxphantom Suite - Coded By Xaatzy - Version 7.0.0
Fitur: Semua user bisa pakai session Telegram yang sama (shared sessions)
GitHub: https://github.com/zzzzoeaa-tech/telegram-reporter
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
# !!! GANTI DENGAN DATA GITHUB KAMU !!!
GITHUB_CONFIG = {
    "owner": "zzzzoeaa-tech",
    "repo": "onyx-databases",
    "branch": "main",
    "token": "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"  # <-- GANTI DENGAN TOKEN ASLI
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
        self.session = None
    
    async def _get_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def read_file(self, path: str) -> Optional[dict]:
        try:
            url = f"{self.base_url}/{path}"
            session = await self._get_session()
            async with session.get(url, headers=self.headers) as resp:
                if resp.status == 404:
                    return None
                if resp.status == 200:
                    data = await resp.json()
                    content = base64.b64decode(data["content"]).decode("utf-8")
                    return json.loads(content)
                return None
        except Exception as e:
            print(f"{Colors.RED}[!] Read error: {e}{Colors.RESET}")
            return None
    
    async def write_file(self, path: str, data: dict, msg: str = "Update") -> bool:
        try:
            url = f"{self.base_url}/{path}"
            content = base64.b64encode(json.dumps(data, indent=2).encode()).decode()
            
            # Get existing file SHA
            existing_sha = None
            session = await self._get_session()
            async with session.get(url, headers=self.headers) as resp:
                if resp.status == 200:
                    existing = await resp.json()
                    existing_sha = existing.get("sha")
            
            payload = {
                "message": msg,
                "content": content,
                "branch": GITHUB_CONFIG["branch"]
            }
            if existing_sha:
                payload["sha"] = existing_sha
            
            async with session.put(url, headers=self.headers, json=payload) as resp:
                return resp.status in [200, 201]
        except Exception as e:
            print(f"{Colors.RED}[!] Write error: {e}{Colors.RESET}")
            return False
    
    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

# ==================== SHARED SESSION MANAGER ====================
class SharedSessionManager:
    """Semua user pakai session yang sama (shared)"""
    
    def __init__(self, db: GitHubDatabase):
        self.db = db
        self.sessions = []  # Shared sessions untuk semua user
        self.local_dir = "shared_sessions"  # Folder lokal untuk session
        self.stats = {"total": 0, "success": 0, "failed": 0}
    
    async def load(self):
        """Load shared sessions dari GitHub"""
        # Buat folder lokal
        if not os.path.exists(self.local_dir):
            os.makedirs(self.local_dir)
        
        # Load sessions dari GitHub
        sessions_data = await self.db.read_file("data/shared_sessions.json")
        if sessions_data:
            self.sessions = sessions_data.get("sessions", [])
            self.stats = sessions_data.get("stats", {"total": 0, "success": 0, "failed": 0})
            print(f"{Colors.GREEN}[✓] Loaded {len(self.sessions)} shared sessions{Colors.RESET}")
        
        # Download session files yang belum ada
        for s in self.sessions:
            local_file = os.path.join(self.local_dir, s["file"])
            if not os.path.exists(local_file):
                session_data = await self.db.read_file(f"sessions/shared/{s['file']}")
                if session_data and "content" in session_data:
                    with open(local_file, "wb") as f:
                        f.write(base64.b64decode(session_data["content"]))
                    print(f"{Colors.GREEN}[✓] Downloaded session: {s['phone']}{Colors.RESET}")
        
        return len(self.sessions)
    
    async def save(self):
        """Save shared sessions ke GitHub"""
        sessions_data = {
            "sessions": self.sessions,
            "stats": self.stats,
            "last_updated": datetime.now().isoformat()
        }
        success = await self.db.write_file("data/shared_sessions.json", sessions_data, "Update shared sessions")
        if success:
            print(f"{Colors.GREEN}[✓] Saved {len(self.sessions)} shared sessions{Colors.RESET}")
        return success
    
    async def add_session(self, phone: str, user_id: int, name: str, session_data: bytes):
        """Add new shared session"""
        session_file = f"{user_id}.session"
        local_path = os.path.join(self.local_dir, session_file)
        
        # Save locally
        with open(local_path, "wb") as f:
            f.write(session_data)
        
        # Upload to GitHub (shared folder)
        await self.db.write_file(f"sessions/shared/{session_file}", 
                                {"content": base64.b64encode(session_data).decode()}, 
                                f"Add shared session: {phone}")
        
        # Add to sessions list
        self.sessions.append({
            "id": user_id,
            "phone": phone,
            "file": session_file,
            "name": name,
            "added_by": "owner",
            "added_at": datetime.now().isoformat(),
            "last_used": datetime.now().isoformat()
        })
        
        await self.save()
        print(f"{Colors.GREEN}[✓] Shared session added: {phone}{Colors.RESET}")
        return True
    
    async def remove_session(self, index: int):
        """Remove shared session"""
        if 0 <= index < len(self.sessions):
            session = self.sessions.pop(index)
            local_path = os.path.join(self.local_dir, session["file"])
            if os.path.exists(local_path):
                os.remove(local_path)
            await self.save()
            print(f"{Colors.GREEN}[✓] Shared session removed: {session['phone']}{Colors.RESET}")
            return True
        return False
    
    async def get_clients(self):
        """Get all active Telegram clients from shared sessions"""
        clients = []
        for s in self.sessions:
            try:
                session_file = os.path.join(self.local_dir, s["file"])
                if os.path.exists(session_file):
                    client = TelegramClient(session_file, API_ID, API_HASH)
                    await client.connect()
                    if await client.is_user_authorized():
                        clients.append((s["id"], client, s))
                        print(f"{Colors.GREEN}[✓] Connected: {s['phone']}{Colors.RESET}")
                    else:
                        await client.disconnect()
                        print(f"{Colors.YELLOW}[!] Not authorized: {s['phone']}{Colors.RESET}")
            except Exception as e:
                print(f"{Colors.RED}[!] Connect failed: {s.get('phone', '?')} - {e}{Colors.RESET}")
        return clients
    
    async def update_stats(self, total_success: int, total_failed: int):
        """Update global stats"""
        self.stats["total"] += total_success + total_failed
        self.stats["success"] += total_success
        self.stats["failed"] += total_failed
        await self.save()

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
                         json={"chat_id": OWNER_CHAT_ID, "text": message}, timeout=5)
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
        return await self.db.write_file("data/devices.json", data, "Register device")
    
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
            if device_id not in data["blocked_devices"]:
                data["blocked_devices"].append(device_id)
            await self.db.write_file("data/devices.json", data, "Block device")
            self.bot.send_notification(device_id, username or "unknown", "3 failed attempts", "temporary")
            return True, "Device blocked after 3 failed attempts"
        
        await self.db.write_file("data/devices.json", data, "Failed attempt")
        return False, f"{3 - device['failed_attempts']} attempts left"
    
    async def reset_attempts(self, device_id: str) -> bool:
        data = await self.get_devices()
        if device_id in data["devices"]:
            data["devices"][device_id]["failed_attempts"] = 0
            return await self.db.write_file("data/devices.json", data, "Reset attempts")
        return False

# ==================== TELEGRAM REPORTER ====================
class TelegramReporter:
    def __init__(self, sm: SharedSessionManager):
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
    
    async def auto_join(self, client, channel):
        try:
            entity = await client.get_entity(channel)
            await client(JoinChannelRequest(entity))
            return True
        except:
            return False
    
    async def report_channel(self, target: str, count: int = 1, username: str = None):
        target_username = self.extract_username(target)
        if not target_username:
            print(f"{Colors.RED}[!] Invalid target{Colors.RESET}")
            return False
        
        clients = await self.sm.get_clients()
        if not clients:
            print(f"{Colors.RED}[!] No active shared sessions!{Colors.RESET}")
            print(f"{Colors.YELLOW}[!] Ask owner to add Telegram sessions first{Colors.RESET}")
            return False
        
        total = 0
        success_count = 0
        failed_count = 0
        
        print(f"\n{Colors.CYAN}[*] Reporting target: @{target_username}{Colors.RESET}")
        print(f"{Colors.CYAN}[*] Using {len(clients)} shared sessions{Colors.RESET}\n")
        
        for uid, client, session in clients:
            try:
                # Try to join if not already joined
                try:
                    entity = await client.get_entity(target_username)
                except:
                    await self.auto_join(client, target_username)
                    entity = await client.get_entity(target_username)
                
                for i in range(count):
                    try:
                        await client(ReportSpamRequest(peer=entity))
                        total += 1
                        success_count += 1
                        print(f"{Colors.CYAN}⣾ [{session['phone']}] Report {i+1}/{count}{Colors.RESET}", end="\r")
                    except FloodWaitError as e:
                        print(f"\n{Colors.YELLOW}[!] Flood wait {e.seconds}s - {session['phone']}{Colors.RESET}")
                        await asyncio.sleep(e.seconds)
                    except Exception as e:
                        print(f"\n{Colors.RED}[!] Failed: {e} - {session['phone']}{Colors.RESET}")
                        failed_count += 1
                    await asyncio.sleep(self.settings["delay"])
                await client.disconnect()
            except Exception as e:
                print(f"{Colors.RED}[!] Error with {session['phone']}: {e}{Colors.RESET}")
                failed_count += count
        
        print()
        await self.sm.update_stats(success_count, failed_count)
        print(f"{Colors.GREEN}[✓] Report complete! Total: {success_count} success, {failed_count} failed{Colors.RESET}")
        return total > 0
    
    async def login_telegram(self):
        """Add new shared session (only owner can do this)"""
        print(f"\n{Colors.CYAN}{'═' * 60}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.YELLOW}▢ ADD SHARED SESSION{Colors.RESET}")
        print(f"{Colors.CYAN}{'═' * 60}{Colors.RESET}")
        print(f"{Colors.DIM}This session will be available for ALL users{Colors.RESET}\n")
        
        phone = input(f"{Colors.GREEN}Phone (+62xxx): {Colors.RESET}").strip()
        if not phone.startswith("+"):
            phone = "+" + phone
        
        # Check if session already exists
        for s in self.sm.sessions:
            if s.get("phone") == phone:
                print(f"{Colors.YELLOW}[!] Session already exists!{Colors.RESET}")
                input("Press Enter...")
                return
        
        session_file = os.path.join(self.sm.local_dir, f"temp_{int(time.time())}.session")
        
        try:
            print(f"{Colors.CYAN}[*] Connecting to Telegram...{Colors.RESET}")
            client = TelegramClient(session_file, API_ID, API_HASH)
            await client.connect()
            
            if not await client.is_user_authorized():
                await client.send_code_request(phone)
                code = input(f"{Colors.GREEN}Code: {Colors.RESET}")
                try:
                    await client.sign_in(phone, code)
                except SessionPasswordNeededError:
                    pwd = input(f"{Colors.GREEN}2FA Password: {Colors.RESET}")
                    await client.sign_in(password=pwd)
            
            me = await client.get_me()
            with open(session_file, "rb") as f:
                content = f.read()
            
            await self.sm.add_session(phone, me.id, me.first_name or "", content)
            os.remove(session_file)
            print(f"{Colors.GREEN}[✓] Shared session added!{Colors.RESET}")
            print(f"{Colors.CYAN}▢ Name: {me.first_name}{Colors.RESET}")
            print(f"{Colors.CYAN}▢ ID: {me.id}{Colors.RESET}")
            print(f"{Colors.GREEN}[✓] Now ALL users can use this session to report!{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.RED}[!] Failed: {e}{Colors.RESET}")
            if os.path.exists(session_file):
                os.remove(session_file)
        input("Press Enter...")

# ==================== OWNER PANEL ====================
class OwnerPanel:
    def __init__(self, um: UserManager, dm: DeviceManager, sm: SharedSessionManager, username: str):
        self.um = um
        self.dm = dm
        self.sm = sm
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
{Colors.GREEN}[9]{Colors.RESET} List Shared Sessions
{Colors.GREEN}[A]{Colors.RESET} Add Shared Session (Telegram)
{Colors.GREEN}[R]{Colors.RESET} Remove Shared Session
{Colors.GREEN}[0]{Colors.RESET} Back

{Colors.CYAN}{'═' * 60}{Colors.RESET}
            """)
            choice = input(f"{Colors.GREEN}Choice: {Colors.RESET}").lower()
            
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
                print(f"{Colors.BOLD}USER LIST{Colors.RESET}")
                print(f"{Colors.CYAN}{'═' * 60}{Colors.RESET}")
                for u in users:
                    status = f"{Colors.RED}BANNED{Colors.RESET}" if u.get("banned") else f"{Colors.GREEN}ACTIVE{Colors.RESET}"
                    role = f"{Colors.YELLOW}[{u['role'].upper()}]{Colors.RESET}" if u['role'] == 'owner' else ""
                    expiry = u.get('expiry', 'Never')[:10] if u.get('expiry') else 'Never'
                    print(f"{Colors.GREEN}{u['username']}{Colors.RESET}: {status} {role}")
                    print(f"  Expiry: {expiry}")
                    print(f"  Reports: {u.get('stats', {}).get('total', 0)}")
                    print()
                input("Press Enter...")
            elif choice == "6":
                devices = await self.dm.get_devices()
                print(f"\n{Colors.CYAN}{'═' * 60}{Colors.RESET}")
                print(f"{Colors.BOLD}DEVICES LIST{Colors.RESET}")
                print(f"{Colors.CYAN}{'═' * 60}{Colors.RESET}")
                devices_list = list(devices["devices"].items())
                for i, (did, info) in enumerate(devices_list, 1):
                    status = f"{Colors.RED}BLOCKED{Colors.RESET}" if info.get("blocked") else f"{Colors.GREEN}ACTIVE{Colors.RESET}"
                    print(f"{i}. {status} - {info['name']}")
                    print(f"   ID: {did[:16]}...")
                    print(f"   Owner: {info['owner']}")
                try:
                    idx = int(input("\nSelect device: ")) - 1
                    if 0 <= idx < len(devices_list):
                        did = devices_list[idx][0]
                        devices["devices"][did]["blocked"] = True
                        if did not in devices["blocked_devices"]:
                            devices["blocked_devices"].append(did)
                        await self.dm.db.write_file("data/devices.json", devices, "Block device")
                        print(f"{Colors.GREEN}[✓] Device blocked{Colors.RESET}")
                except:
                    pass
                input("Press Enter...")
            elif choice == "7":
                devices = await self.dm.get_devices()
                blocked = devices["blocked_devices"]
                if not blocked:
                    print(f"{Colors.YELLOW}[!] No blocked devices{Colors.RESET}")
                    input("Press Enter...")
                    continue
                print(f"\n{Colors.CYAN}{'═' * 60}{Colors.RESET}")
                print(f"{Colors.BOLD}BLOCKED DEVICES{Colors.RESET}")
                print(f"{Colors.CYAN}{'═' * 60}{Colors.RESET}")
                for i, did in enumerate(blocked, 1):
                    info = devices["devices"].get(did, {})
                    print(f"{i}. {info.get('name', 'Unknown')} - {did[:16]}...")
                try:
                    idx = int(input("\nSelect device: ")) - 1
                    if 0 <= idx < len(blocked):
                        did = blocked[idx]
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
                print(f"{Colors.BOLD}ALL DEVICES{Colors.RESET}")
                print(f"{Colors.CYAN}{'═' * 60}{Colors.RESET}")
                for did, info in devices["devices"].items():
                    status = f"{Colors.RED}BLOCKED{Colors.RESET}" if info.get("blocked") else f"{Colors.GREEN}ACTIVE{Colors.RESET}"
                    print(f"{Colors.CYAN}Device:{Colors.RESET} {info['name']} [{status}]")
                    print(f"  ID: {did}")
                    print(f"  Owner: {info['owner']}")
                    print(f"  Failed: {info.get('failed_attempts', 0)}")
                    print()
                input("Press Enter...")
            elif choice == "9":
                print(f"\n{Colors.CYAN}{'═' * 60}{Colors.RESET}")
                print(f"{Colors.BOLD}SHARED SESSIONS{Colors.RESET}")
                print(f"{Colors.CYAN}{'═' * 60}{Colors.RESET}\n")
                if not self.sm.sessions:
                    print(f"{Colors.YELLOW}No shared sessions{Colors.RESET}")
                else:
                    for i, s in enumerate(self.sm.sessions, 1):
                        print(f"{Colors.GREEN}{i}.{Colors.RESET} {s.get('phone', '?')} | {s.get('name', '?')}")
                        print(f"   Added: {s.get('added_at', '?')[:16]}")
                        print(f"   Used by: ALL USERS")
                        print()
                input("Press Enter...")
            elif choice == "a":
                # Add shared session - panggil fungsi dari reporter
                reporter = TelegramReporter(self.sm)
                await reporter.login_telegram()
            elif choice == "r":
                if not self.sm.sessions:
                    print(f"{Colors.YELLOW}[!] No shared sessions{Colors.RESET}")
                    input("Press Enter...")
                    continue
                print(f"\n{Colors.CYAN}{'═' * 60}{Colors.RESET}")
                print(f"{Colors.BOLD}REMOVE SHARED SESSION{Colors.RESET}")
                print(f"{Colors.CYAN}{'═' * 60}{Colors.RESET}\n")
                for i, s in enumerate(self.sm.sessions, 1):
                    print(f"{Colors.GREEN}{i}.{Colors.RESET} {s.get('phone', '?')} | {s.get('name', '?')}")
                try:
                    idx = int(input(f"\n{Colors.GREEN}Select (0=cancel): {Colors.RESET}")) - 1
                    if idx >= 0:
                        await self.sm.remove_session(idx)
                except:
                    pass
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
        self.sm = SharedSessionManager(self.db)  # Shared sessions untuk semua user
        self.reporter = None
    
    async def run(self):
        print(f"{Colors.CYAN}[*] Registering device...{Colors.RESET}")
        await self.dm.register_device(self.username, self.device_id)
        
        print(f"{Colors.CYAN}[*] Loading shared sessions from GitHub...{Colors.RESET}")
        await self.sm.load()
        
        self.reporter = TelegramReporter(self.sm)
        
        while True:
            os.system("clear" if os.name == "posix" else "cls")
            print(ASCII_ART)
            
            # Get current time
            now = datetime.now()
            time_str = now.strftime("%H:%M:%S")
            date_str = now.strftime("%A, %d %B %Y")
            
            rate = (self.sm.stats["success"] / self.sm.stats["total"] * 100) if self.sm.stats["total"] > 0 else 0
            
            owner_menu = f"\n{Colors.GREEN}[A]{Colors.RESET} ▢ Owner Panel 👑" if self.role == "owner" else ""
            
            print(f"""
{Colors.CYAN}{'═' * 60}{Colors.RESET}
{Colors.BOLD}{Colors.YELLOW}▢ NOTIFICATION{Colors.RESET}
{Colors.CYAN}{'═' * 60}{Colors.RESET}
{Colors.GREEN}[ • ]{Colors.RESET} Status       : {Colors.YELLOW}Connected to GitHub{Colors.RESET}
{Colors.GREEN}[ • ]{Colors.RESET} Time         : {Colors.CYAN}{time_str}{Colors.RESET}
{Colors.GREEN}[ • ]{Colors.RESET} Date         : {Colors.CYAN}{date_str}{Colors.RESET}
{Colors.GREEN}[ • ]{Colors.RESET} Device ID    : {Colors.MAGENTA}{self.device_id[:16]}...{Colors.RESET}
{Colors.GREEN}[ • ]{Colors.RESET} Shared Sessions: {Colors.CYAN}{len(self.sm.sessions)}{Colors.RESET}

{Colors.CYAN}{'═' * 60}{Colors.RESET}
{Colors.BOLD}{Colors.YELLOW}▢ MAIN MENU{Colors.RESET}
{Colors.CYAN}{'═' * 60}{Colors.RESET}

{Colors.GREEN}[1]{Colors.RESET} ▢ Report Channel/Group
{Colors.GREEN}[2]{Colors.RESET} ▢ Report Post
{Colors.GREEN}[3]{Colors.RESET} ▢ Report Account
{Colors.GREEN}[4]{Colors.RESET} ▢ Report Bot
{Colors.GREEN}[5]{Colors.RESET} ▢ Statistics
{owner_menu}
{Colors.GREEN}[0]{Colors.RESET} ▢ Logout

{Colors.CYAN}{'═' * 60}{Colors.RESET}
{Colors.DIM}User: {self.username} ({self.role}) | Shared Sessions: {len(self.sm.sessions)} | Total Reports: {self.sm.stats['total']} | Rate: {rate:.0f}%{Colors.RESET}
{Colors.CYAN}{'═' * 60}{Colors.RESET}
            """)
            
            choice = input(f"{Colors.GREEN}Choice: {Colors.RESET}").lower()
            
            if choice == "1":
                target = input(f"{Colors.GREEN}Target (@username or link): {Colors.RESET}")
                cnt = int(input(f"{Colors.GREEN}Count per session (1-100): {Colors.RESET}") or "1")
                await self.reporter.report_channel(target, min(cnt, 100), self.username)
                input("Press Enter...")
            elif choice == "2":
                target = input(f"{Colors.GREEN}Post link: {Colors.RESET}")
                cnt = int(input(f"{Colors.GREEN}Count per session (1-100): {Colors.RESET}") or "1")
                channel = re.search(r"t\.me/([a-zA-Z0-9_]+)", target)
                if channel:
                    await self.reporter.report_channel(channel.group(1), min(cnt, 100), self.username)
                else:
                    print(f"{Colors.RED}[!] Invalid link{Colors.RESET}")
                input("Press Enter...")
            elif choice == "3":
                target = input(f"{Colors.GREEN}Username: {Colors.RESET}")
                cnt = int(input(f"{Colors.GREEN}Count per session (1-100): {Colors.RESET}") or "1")
                await self.reporter.report_channel(target, min(cnt, 100), self.username)
                input("Press Enter...")
            elif choice == "4":
                target = input(f"{Colors.GREEN}Bot username: {Colors.RESET}")
                cnt = int(input(f"{Colors.GREEN}Count per session (1-100): {Colors.RESET}") or "1")
                await self.reporter.report_channel(target, min(cnt, 100), self.username)
                input("Press Enter...")
            elif choice == "5":
                print(f"""
{Colors.CYAN}{'═' * 60}{Colors.RESET}
{Colors.BOLD}{Colors.YELLOW}▢ STATISTICS{Colors.RESET}
{Colors.CYAN}{'═' * 60}{Colors.RESET}

{Colors.GREEN}Total Reports (All Users):{Colors.RESET} {self.sm.stats['total']}
{Colors.GREEN}Success:{Colors.RESET} {self.sm.stats['success']}
{Colors.GREEN}Failed:{Colors.RESET} {self.sm.stats['failed']}
{Colors.GREEN}Rate:{Colors.RESET} {rate:.0f}%
{Colors.GREEN}Shared Sessions:{Colors.RESET} {len(self.sm.sessions)}
{Colors.CYAN}{'═' * 60}{Colors.RESET}
                """)
                input("Press Enter...")
            elif choice == "a" and self.role == "owner":
                owner = OwnerPanel(self.um, self.dm, self.sm, self.username)
                await owner.show()
            elif choice == "0":
                print(f"\n{Colors.GREEN}Goodbye!{Colors.RESET}")
                await self.db.close()
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
    return hashlib.sha256(f"{hostname}_{username}_{time.time()}".encode()).hexdigest()[:32]

async def login_screen():
    db = GitHubDatabase()
    um = UserManager(db)
    dm = DeviceManager(db)
    device_id = get_device_id()
    
    attempts = 0
    while attempts < 3:
        os.system("clear" if os.name == "posix" else "cls")
        print(ASCII_ART)
        print(f"\n{Colors.CYAN}{'═' * 60}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.YELLOW}▢ LOGIN{Colors.RESET}")
        print(f"{Colors.CYAN}{'═' * 60}{Colors.RESET}\n")
        
        # Check if device blocked
        blocked, msg = await dm.is_blocked(device_id)
        if blocked:
            print(f"{Colors.RED}⚠️ {msg}{Colors.RESET}")
            input("\nPress Enter...")
            await db.close()
            return None, None, None
        
        username = input(f"{Colors.GREEN}Username: {Colors.RESET}")
        password = input(f"{Colors.GREEN}Password: {Colors.RESET}")
        
        verified, user_data = await um.verify_user(username, password, device_id)
        
        if verified:
            await dm.reset_attempts(device_id)
            print(f"\n{Colors.GREEN}✅ Welcome back, {username}!{Colors.RESET}")
            await asyncio.sleep(1)
            await db.close()
            return username, user_data.get("role", "user"), device_id
        else:
            attempts += 1
            blocked, msg = await dm.record_failed(device_id, username)
            print(f"\n{Colors.RED}❌ {user_data.get('error', 'Login failed')}{Colors.RESET}")
            if blocked:
                print(f"{Colors.RED}⚠️ {msg}{Colors.RESET}")
                input("\nPress Enter...")
                await db.close()
                return None, None, None
            print(f"{Colors.YELLOW}⚠️ {3 - attempts} attempts left{Colors.RESET}")
            await asyncio.sleep(1)
    
    print(f"\n{Colors.RED}🔒 Device blocked!{Colors.RESET}")
    input("\nPress Enter...")
    await db.close()
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
