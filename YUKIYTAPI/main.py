"""
========================================================================
  ʏᴜᴋɪ ʏᴛ ᴀᴘɪ - ᴀᴅᴠᴀɴᴄᴇᴅ ᴍᴇᴅɪᴀ ꜱᴛʀᴇᴀᴍɪɴɢ ᴇɴɢɪɴᴇ
========================================================================
  © 2026 ᴋᴀɪᴛᴏ | ʜᴇʟʟꜰɪʀᴇᴅᴇᴠꜱ. ᴀʟʟ ʀɪɢʜᴛꜱ ʀᴇꜱᴇʀᴠᴇᴅ.
  
  ᴡᴀʀɴɪɴɢ: ᴅᴏ ɴᴏᴛ ᴇᴅɪᴛ, ᴍᴏᴅɪꜰʏ, ᴏʀ ʀᴇᴍᴏᴠᴇ ᴛʜɪꜱ ʜᴇᴀᴅᴇʀ.
  ᴛʜɪꜱ ᴄᴏᴅᴇʙᴀꜱᴇ ɪꜱ ᴘʀᴏᴛᴇᴄᴛᴇᴅ ʙʏ ᴀɴ ᴀᴄᴛɪᴠᴇ ᴀɴᴛɪ-ᴛᴀᴍᴘᴇʀ ᴍᴇᴄʜᴀɴɪꜱᴍ. 
  ʀᴇᴍᴏᴠɪɴɢ ᴛʜɪꜱ ᴄᴏᴘʏʀɪɢʜᴛ ɴᴏᴛɪᴄᴇ ᴡɪʟʟ ᴛʀɪɢɢᴇʀ ᴀ ꜱʏꜱᴛᴇᴍ-ʟᴇᴠᴇʟ 
  ꜰᴀᴛᴀʟ ᴇʀʀᴏʀ ᴀɴᴅ ᴘᴇʀᴍᴀɴᴇɴᴛʟʏ ᴘʀᴇᴠᴇɴᴛ ᴛʜᴇ ᴀᴘɪ ꜰʀᴏᴍ ʀᴜɴɴɪɴɢ.
========================================================================
"""

import sys

#
if __doc__ is None or "© 2026 ᴋᴀɪᴛᴏ | ʜᴇʟʟꜰɪʀᴇᴅᴇᴠꜱ. ᴀʟʟ ʀɪɢʜᴛꜱ ʀᴇꜱᴇʀᴠᴇᴅ." not in __doc__:
    print("\n[!] ꜰᴀᴛᴀʟ ᴇʀʀᴏʀ: ᴄᴏᴘʏʀɪɢʜᴛ ᴛᴀᴍᴘᴇʀɪɴɢ ᴅᴇᴛᴇᴄᴛᴇᴅ.")
    print("[!] ᴛʜᴇ ʜᴇʟʟꜰɪʀᴇᴅᴇᴠꜱ ᴄᴏᴘʏʀɪɢʜᴛ ʜᴇᴀᴅᴇʀ ʜᴀꜱ ʙᴇᴇɴ ᴍᴏᴅɪꜰɪᴇᴅ ᴏʀ ʀᴇᴍᴏᴠᴇᴅ.")
    print("[!] ᴀᴘɪ ᴇxᴇᴄᴜᴛɪᴏɴ ʙʟᴏᴄᴋᴇᴅ. ꜱʏꜱᴛᴇᴍ ᴇxɪᴛɪɴɢ...\n")
    sys.exit(1)

import os
import re
import time
import uuid
import asyncio
from fastapi import FastAPI, BackgroundTasks, Header, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse

from YUKIYTAPI.database.stats import init_db, add_download, get_stats

app = FastAPI(title="YUKI YT API")

BASE_DIR     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DIR    = os.path.join(BASE_DIR, "YUKIYTAPI", "saved")
COOKIES_FILE = os.path.join(BASE_DIR, "cookies.txt")
os.makedirs(CACHE_DIR, exist_ok=True)

init_db()

TOKENS     = {}
START_TIME = time.time()

# ─────────────────────────────────────────
# HELPER: Extract video ID from any YT URL
# ─────────────────────────────────────────
def extract_video_id(url: str) -> str:
    """
    Handles all YouTube URL formats:
      - Plain ID:          dQw4w9WgXcQ
      - Standard:          https://youtube.com/watch?v=dQw4w9WgXcQ
      - Short:             https://youtu.be/dQw4w9WgXcQ
      - Shorts:            https://youtube.com/shorts/dQw4w9WgXcQ
      - Embed:             https://youtube.com/embed/dQw4w9WgXcQ
      - With extra params: ?v=ID&list=...&t=...
    """
    # Already a plain 11-char video ID
    if re.match(r'^[a-zA-Z0-9_-]{11}$', url):
        return url

    patterns = [
        r'(?:v=)([a-zA-Z0-9_-]{11})',       # ?v=ID  (standard / mobile)
        r'youtu\.be/([a-zA-Z0-9_-]{11})',    # youtu.be/ID
        r'/shorts/([a-zA-Z0-9_-]{11})',      # /shorts/ID
        r'/embed/([a-zA-Z0-9_-]{11})',       # /embed/ID
        r'/live/([a-zA-Z0-9_-]{11})',        # /live/ID
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    # Fallback: return as-is (yt-dlp can handle full URLs too)
    return url


# ─────────────────────────────────────────
# HELPER: Find cached file (any extension)
# ─────────────────────────────────────────
def find_cached_file(video_id: str, type: str) -> str | None:
    """
    yt-dlp may save as .m4a, .opus, .webm etc depending on availability.
    Check all known extensions so we don't miss a valid cache hit.
    """
    if type == "audio":
        exts = ["m4a", "opus", "webm", "mp3", "ogg"]
    else:
        exts = ["mp4", "mkv", "webm"]

    for ext in exts:
        path = os.path.join(CACHE_DIR, f"{video_id}.{ext}")
        if os.path.exists(path) and os.path.getsize(path) > 0:
            return path
    return None


# ─────────────────────────────────────────
# BACKGROUND: temp → cache (after response sent)
# ─────────────────────────────────────────
def _move_to_cache(tmp_path: str, cache_path: str) -> None:
    try:
        if os.path.exists(tmp_path) and os.path.getsize(tmp_path) > 0:
            os.replace(tmp_path, cache_path)
    except Exception:
        try:
            os.remove(tmp_path)
        except Exception:
            pass


# ─────────────────────────────────────────
# HOME
# ─────────────────────────────────────────
@app.get("/")
async def home(request: Request):
    uptime = round(time.time() - START_TIME, 2)
    return JSONResponse({
        "status":  "Running...",
        "owner":   "YUKIMUSIC",
        "uptime":  f"{uptime}s",
        "message": "Welcome to YUKI API",
    })


# ─────────────────────────────────────────
# STATS
# ─────────────────────────────────────────
@app.get("/stats")
async def api_stats(request: Request):
    total_dl, cache_mb = get_stats()
    return JSONResponse({
        "status":               "success",
        "total_song_downloads": total_dl,
        "total_cache_size_mb":  cache_mb,
        "active_tokens":        len(TOKENS),
    })


# ─────────────────────────────────────────
# TOKEN GENERATE
# ─────────────────────────────────────────
@app.get("/download")
async def generate_token(request: Request, url: str, type: str = "audio"):
    # FIX: Proper video ID extraction from any URL format
    video_id   = extract_video_id(url)
    yuki_token = f"YUKIMusic{uuid.uuid4().hex[:16]}YukiBots"
    TOKENS[yuki_token] = {
        "video_id": video_id,
        "type":     type,
        "expires":  time.time() + 300,  # FIX: 5 min instead of 60s
    }
    return JSONResponse({
        "status":         "success",
        "video_id":       video_id,
        "download_token": yuki_token,
        "usage":          "Use token parameter in /stream endpoint",
    })


# ─────────────────────────────────────────
# STREAM  (download → serve → cache in bg)
# ─────────────────────────────────────────
@app.get("/stream/{video_id}")
async def stream_music(
    request:          Request,
    video_id:         str,
    background_tasks: BackgroundTasks,
    type:             str = "audio",
    token:            str = None,                          # query param
    x_download_token: str = Header(None),                  # header (Youtube.py sends this)
):
    # ── Auth — accept token from either query param OR header ─────────────────
    actual_token = token or x_download_token
    if not actual_token or actual_token not in TOKENS:
        raise HTTPException(status_code=401, detail="Invalid Token Access Denied")

    token_data = TOKENS[actual_token]
    if time.time() > token_data["expires"] or token_data["video_id"] != video_id:
        TOKENS.pop(actual_token, None)
        raise HTTPException(status_code=401, detail="Token Expired")

    del TOKENS[actual_token]

    # ── Cache hit → serve instantly (FIX: checks all extensions) ─────────────
    cached = find_cached_file(video_id, type)
    if cached:
        add_download()
        return FileResponse(
            cached,
            media_type="audio/mp4" if type == "audio" else "video/mp4",
        )

    # ── Cache miss → yt-dlp download to temp ──────────────────────────────────
    outtmpl = os.path.join(CACHE_DIR, f"{video_id}.tmp.%(ext)s")

    if type == "audio":
        cmd = [
            "yt-dlp",
            "--cookies", COOKIES_FILE,
            "--js-runtimes", "node",
            "--remote-components", "ejs:github",
            "--extractor-args", "youtube:player_client=web_creator,web;youtubepot-bgutilhttp:base_url=http://127.0.0.1:4416",
            "-f", "bestaudio[ext=m4a]/bestaudio[ext=opus]/bestaudio/best",
            "-o", outtmpl,
            "--quiet",
            video_id,
        ]
    else:
        cmd = [
            "yt-dlp",
            "--cookies", COOKIES_FILE,
            "--js-runtimes", "node",
            "--remote-components", "ejs:github",
            "--extractor-args", "youtube:player_client=web_creator,web;youtubepot-bgutilhttp:base_url=http://127.0.0.1:4416",
            "-f", "(bestvideo[ext=mp4]+bestaudio[ext=m4a])/best[ext=mp4]/best",
            "-o", outtmpl,
            "--quiet",
            video_id,
        ]

    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        _, stderr = await process.communicate()

        if process.returncode != 0:
            raise HTTPException(
                status_code=500,
                detail=f"yt-dlp error: {stderr.decode()[:300]}",
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # ── Find actual downloaded file (ext may vary e.g. opus) ─────────────────
    actual_tmp = None
    for fname in os.listdir(CACHE_DIR):
        if fname.startswith(f"{video_id}.tmp.") and not fname.endswith(".tmp"):
            actual_tmp = os.path.join(CACHE_DIR, fname)
            break

    if not actual_tmp or not os.path.exists(actual_tmp):
        raise HTTPException(status_code=500, detail="Download failed — file not found")

    actual_ext  = actual_tmp.rsplit(".", 1)[-1]
    final_cache = os.path.join(CACHE_DIR, f"{video_id}.{actual_ext}")

    add_download()

    # ── Serve temp file → background moves it to cache ───────────────────────
    background_tasks.add_task(_move_to_cache, actual_tmp, final_cache)

    return FileResponse(
        actual_tmp,
        media_type="audio/mp4" if type == "audio" else "video/mp4",
    )
  
