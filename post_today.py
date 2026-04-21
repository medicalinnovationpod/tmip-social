#!/usr/bin/env python3
"""
Post today's scheduled clip to Instagram and YouTube.
Runs daily via GitHub Actions at 12pm EST.
"""

import os
import re
import sys
import json
import time
import base64
import tempfile
import subprocess
from datetime import date, datetime, timezone
from pathlib import Path

import requests

GITHUB_REPO = "medicalinnovationpod/tmip-social"
CLIPS_GITHUB_REPO = os.environ.get("CLIPS_GITHUB_REPO", "medicalinnovationpod/tmip-clips")
IG_BASE = "https://graph.instagram.com/v21.0"


def env(key):
    val = os.environ.get(key)
    if not val:
        raise RuntimeError(f"Missing required environment variable: {key}")
    return val


# ── Instagram ────────────────────────────────────────────────────────────────

def refresh_instagram_token(token):
    resp = requests.get(
        f"{IG_BASE}/refresh_access_token",
        params={"grant_type": "ig_refresh_token", "access_token": token},
        timeout=15
    )
    if resp.ok:
        new_token = resp.json().get("access_token", token)
        if new_token != token:
            print("  Instagram token refreshed.")
        return new_token
    print(f"  Warning: token refresh failed ({resp.status_code}), continuing with existing token.")
    return token


def update_github_secret(secret_name, secret_value, gh_pat):
    """Update a GitHub Actions secret via the GitHub API."""
    if not gh_pat:
        print("  Warning: GH_PAT not set — skipping secret update.")
        return
    try:
        from nacl import public, encoding
    except ImportError:
        print("  Warning: PyNaCl not installed — skipping secret update.")
        return

    headers = {
        "Authorization": f"Bearer {gh_pat}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    # Get repo public key
    resp = requests.get(
        f"https://api.github.com/repos/{GITHUB_REPO}/actions/secrets/public-key",
        headers=headers, timeout=15
    )
    resp.raise_for_status()
    key_data = resp.json()

    pk = public.PublicKey(key_data["key"].encode(), encoding.Base64Encoder)
    encrypted = public.SealedBox(pk).encrypt(secret_value.encode())

    resp = requests.put(
        f"https://api.github.com/repos/{GITHUB_REPO}/actions/secrets/{secret_name}",
        headers=headers,
        json={"encrypted_value": base64.b64encode(encrypted).decode(), "key_id": key_data["key_id"]},
        timeout=15
    )
    resp.raise_for_status()
    print(f"  Updated GitHub Secret: {secret_name}")


def post_instagram_reel(video_url, caption, user_id, token):
    """Create container → wait → publish. Returns media_id."""

    # 1. Create container
    print("  Creating media container...")
    resp = requests.post(
        f"{IG_BASE}/{user_id}/media",
        params={
            "media_type": "REELS",
            "video_url": video_url,
            "caption": caption,
            "access_token": token,
        },
        timeout=30
    )
    resp.raise_for_status()
    container_id = resp.json()["id"]
    print(f"  Container ID: {container_id}")

    # 2. Poll until processed
    print("  Waiting for Instagram to process video...", end="", flush=True)
    for _ in range(40):
        time.sleep(10)
        resp = requests.get(
            f"{IG_BASE}/{container_id}",
            params={"fields": "status_code,status", "access_token": token},
            timeout=15
        )
        resp.raise_for_status()
        status = resp.json().get("status_code", "")
        print(f" {status}", end="", flush=True)
        if status == "FINISHED":
            break
        if status == "ERROR":
            raise RuntimeError(f"Instagram processing error: {resp.json()}")
    else:
        raise RuntimeError("Instagram video processing timed out after ~7 minutes.")
    print()

    # 3. Publish
    print("  Publishing...")
    resp = requests.post(
        f"{IG_BASE}/{user_id}/media_publish",
        params={"creation_id": container_id, "access_token": token},
        timeout=30
    )
    resp.raise_for_status()
    media_id = resp.json()["id"]
    print(f"  ✓ Published — media ID: {media_id}")
    return media_id


def post_instagram_comment(media_id, text, token):
    resp = requests.post(
        f"{IG_BASE}/{media_id}/comments",
        params={"message": text, "access_token": token},
        timeout=15
    )
    if resp.ok:
        print(f"  ✓ Comment posted")
    else:
        print(f"  Warning: comment failed ({resp.status_code}): {resp.text[:200]}")


# ── YouTube ───────────────────────────────────────────────────────────────────

def get_youtube_access_token(client_id, client_secret, refresh_token):
    resp = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        },
        timeout=15
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def post_youtube_short(video_path, title, description, tags, access_token):
    """Upload a YouTube Short via resumable upload. Returns video URL."""
    headers = {"Authorization": f"Bearer {access_token}"}

    metadata = {
        "snippet": {
            "title": title[:100],
            "description": description,
            "tags": tags,
            "categoryId": "22",  # People & Blogs
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
        },
    }

    # Initiate resumable upload
    video_size = os.path.getsize(video_path)
    resp = requests.post(
        "https://www.googleapis.com/upload/youtube/v3/videos"
        "?uploadType=resumable&part=snippet,status",
        headers={
            **headers,
            "Content-Type": "application/json",
            "X-Upload-Content-Type": "video/mp4",
            "X-Upload-Content-Length": str(video_size),
        },
        json=metadata,
        timeout=30
    )
    resp.raise_for_status()
    upload_url = resp.headers["Location"]

    # Upload file
    print(f"  Uploading {video_size / 1024 / 1024:.1f} MB to YouTube...")
    with open(video_path, "rb") as f:
        resp = requests.put(
            upload_url,
            headers={"Content-Type": "video/mp4", "Content-Length": str(video_size)},
            data=f,
            timeout=300
        )
    resp.raise_for_status()
    video_id = resp.json()["id"]
    url = f"https://youtube.com/shorts/{video_id}"
    print(f"  ✓ Uploaded — {url}")
    return url


# ── GitHub clip cleanup ───────────────────────────────────────────────────────

def delete_clip_from_github(filename, gh_pat):
    """Delete a clip file from the public clips repo after confirmed posting."""
    if not gh_pat:
        return
    headers = {
        "Authorization": f"Bearer {gh_pat}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    resp = requests.get(
        f"https://api.github.com/repos/{CLIPS_GITHUB_REPO}/contents/{filename}",
        headers=headers, timeout=15
    )
    if resp.status_code == 404:
        return
    if not resp.ok:
        print(f"  Warning: could not fetch clip SHA for deletion ({resp.status_code})")
        return
    sha = resp.json()["sha"]
    del_resp = requests.delete(
        f"https://api.github.com/repos/{CLIPS_GITHUB_REPO}/contents/{filename}",
        headers=headers,
        json={"message": f"Remove {filename} after posting", "sha": sha},
        timeout=15
    )
    if del_resp.ok:
        print(f"  ✓ Deleted {filename} from {CLIPS_GITHUB_REPO}")
    else:
        print(f"  Warning: clip deletion failed ({del_resp.status_code})")


# ── TikTok ───────────────────────────────────────────────────────────────────

def get_tiktok_access_token(client_key, client_secret, refresh_token):
    resp = requests.post(
        "https://open.tiktokapis.com/v2/oauth/token/",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "client_key": client_key,
            "client_secret": client_secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        },
        timeout=15
    )
    resp.raise_for_status()
    data = resp.json().get("data", resp.json())
    new_refresh = data.get("refresh_token")
    return data["access_token"], new_refresh


def post_tiktok_video(video_url, caption, access_token):
    """Post a TikTok video via PULL_FROM_URL. Returns publish_id."""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=UTF-8",
    }

    # Initiate upload
    resp = requests.post(
        "https://open.tiktokapis.com/v2/post/publish/video/init/",
        headers=headers,
        json={
            "post_info": {
                "title": caption[:2200],
                "privacy_level": "PUBLIC_TO_EVERYONE",
                "disable_duet": False,
                "disable_comment": False,
                "disable_stitch": False,
            },
            "source_info": {
                "source": "PULL_FROM_URL",
                "video_url": video_url,
            },
        },
        timeout=30
    )
    resp.raise_for_status()
    publish_id = resp.json()["data"]["publish_id"]
    print(f"  TikTok publish_id: {publish_id}")

    # Poll until published (TikTok processes async)
    print("  Waiting for TikTok to process...", end="", flush=True)
    for _ in range(30):
        time.sleep(10)
        status_resp = requests.post(
            "https://open.tiktokapis.com/v2/post/publish/status/fetch/",
            headers=headers,
            json={"publish_id": publish_id},
            timeout=15
        )
        if not status_resp.ok:
            print(f" (status check failed)", end="", flush=True)
            continue
        status = status_resp.json().get("data", {}).get("status", "")
        print(f" {status}", end="", flush=True)
        if status == "PUBLISH_COMPLETE":
            print()
            print("  ✓ Published to TikTok")
            return publish_id
        if status in ("FAILED", "CANCELED"):
            raise RuntimeError(f"TikTok publish failed: {status_resp.json()}")
    print()
    print("  Warning: TikTok status polling timed out — video may still be processing.")
    return publish_id


def post_tiktok_comment(publish_id, text, access_token):
    # TikTok comment API requires video_id, not publish_id — skip for now
    # Comments can be added manually or via a separate video lookup step
    pass


# ── Schedule & logging ────────────────────────────────────────────────────────

def load_schedule():
    with open("schedule.json") as f:
        return json.load(f)


def save_schedule(schedule):
    with open("schedule.json", "w") as f:
        json.dump(schedule, f, indent=2)


def append_log(entry):
    log_path = Path("logs/post_log.json")
    log_path.parent.mkdir(exist_ok=True)
    logs = json.loads(log_path.read_text()) if log_path.exists() else []
    logs.append(entry)
    log_path.write_text(json.dumps(logs, indent=2))


def commit_and_push(message):
    remote = f"https://x-access-token:{os.environ['GITHUB_TOKEN']}@github.com/{GITHUB_REPO}.git"
    subprocess.run(["git", "remote", "set-url", "origin", remote], check=True)
    subprocess.run(["git", "add", "schedule.json", "logs/"], check=True)
    result = subprocess.run(["git", "diff", "--cached", "--quiet"])
    if result.returncode == 0:
        print("  Nothing to commit.")
        return
    subprocess.run(["git", "commit", "-m", message], check=True)
    subprocess.run(["git", "push"], check=True)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    today = date.today().isoformat()
    now_utc = datetime.now(timezone.utc).isoformat()
    print(f"\n=== TMIP Social Poster — {today} ===\n")

    schedule = load_schedule()
    pending = [p for p in schedule.get("posts", []) if p["date"] == today and p["status"] == "pending"]

    if not pending:
        print("No posts scheduled for today. Nothing to do.")
        return

    post = pending[0]
    print(f"Today's post: Clip {post['clip_number']} — {post['title']}")
    print(f"Episode: {post['episode']}\n")

    # Credentials
    ig_user_id = env("INSTAGRAM_USER_ID")
    ig_token = env("INSTAGRAM_ACCESS_TOKEN")
    yt_client_id = env("YOUTUBE_CLIENT_ID")
    yt_client_secret = env("YOUTUBE_CLIENT_SECRET")
    yt_refresh_token = env("YOUTUBE_REFRESH_TOKEN")
    tt_client_key = env("TIKTOK_CLIENT_KEY")
    tt_client_secret = env("TIKTOK_CLIENT_SECRET")
    tt_refresh_token = env("TIKTOK_REFRESH_TOKEN")
    gh_pat = os.environ.get("GH_PAT", "")

    log_entry = {
        "date": today,
        "posted_at": now_utc,
        "episode": post["episode"],
        "clip_number": post["clip_number"],
        "title": post["title"],
        "instagram": None,
        "youtube": None,
        "tiktok": None,
        "error": None,
    }

    try:
        # Refresh Instagram token
        print("Refreshing Instagram token...")
        new_token = refresh_instagram_token(ig_token)
        if new_token != ig_token:
            ig_token = new_token
            update_github_secret("INSTAGRAM_ACCESS_TOKEN", new_token, gh_pat)

        # Download clip to temp file (needed for YouTube upload)
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            tmp_path = tmp.name
        print(f"\nDownloading clip...")
        resp = requests.get(post["r2_url"], stream=True, timeout=120)
        resp.raise_for_status()
        with open(tmp_path, "wb") as f:
            for chunk in resp.iter_content(8192):
                f.write(chunk)
        print(f"  ✓ {os.path.getsize(tmp_path) / 1024 / 1024:.1f} MB")

        # Post to Instagram
        print("\nPosting to Instagram...")
        media_id = post_instagram_reel(post["r2_url"], post["ig_caption"], ig_user_id, ig_token)
        post_instagram_comment(media_id, f"Listen now: {post['episode_url']}", ig_token)
        log_entry["instagram"] = media_id

        # Post to YouTube
        print("\nPosting to YouTube...")
        yt_token = get_youtube_access_token(yt_client_id, yt_client_secret, yt_refresh_token)
        yt_url = post_youtube_short(
            tmp_path,
            post["title"],
            post["yt_description"],
            post["hashtags"],
            yt_token
        )
        log_entry["youtube"] = yt_url

        # Post to TikTok
        print("\nPosting to TikTok...")
        tiktok_caption = post.get("tiktok_caption") or post["ig_caption"]
        tt_token, new_tt_refresh = get_tiktok_access_token(tt_client_key, tt_client_secret, tt_refresh_token)
        if new_tt_refresh and new_tt_refresh != tt_refresh_token:
            update_github_secret("TIKTOK_REFRESH_TOKEN", new_tt_refresh, gh_pat)
        tt_publish_id = post_tiktok_video(post["r2_url"], tiktok_caption, tt_token)
        log_entry["tiktok"] = tt_publish_id

        # Mark as posted
        for p in schedule["posts"]:
            if p["date"] == today and p["clip_number"] == post["clip_number"]:
                p.update({
                    "status": "posted",
                    "posted_at": now_utc,
                    "ig_media_id": media_id,
                    "yt_url": yt_url,
                    "tt_publish_id": tt_publish_id,
                })

        save_schedule(schedule)
        append_log(log_entry)
        commit_and_push(f"Posted: {post['episode']} Clip {post['clip_number']} ({today})")

        # Delete clip from public GitHub hosting repo now that all platforms are posted
        clip_num = post["clip_number"]
        ep_num = re.search(r"\d+", post["episode"]).group()
        clip_filename = f"episode-{ep_num}-clip-{int(clip_num):02d}.mp4"
        print(f"\nCleaning up {clip_filename} from clips repo...")
        delete_clip_from_github(clip_filename, gh_pat)

        print(f"\n✓ All done! Instagram, YouTube, and TikTok posted successfully.")

    except Exception as e:
        error_msg = str(e)
        print(f"\n✗ Error: {error_msg}")
        log_entry["error"] = error_msg
        for p in schedule["posts"]:
            if p["date"] == today and p["clip_number"] == post["clip_number"]:
                p["status"] = "failed"
                p["error"] = error_msg
        save_schedule(schedule)
        append_log(log_entry)
        try:
            commit_and_push(f"Failed: {post['episode']} Clip {post['clip_number']} ({today})")
        except Exception:
            pass
        sys.exit(1)  # Non-zero exit → GitHub Actions sends failure email

    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


if __name__ == "__main__":
    main()
