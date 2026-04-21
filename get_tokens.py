#!/usr/bin/env python3
"""
One-time helper to obtain OAuth tokens for Instagram, YouTube, and TikTok.

Run this locally. It will print the tokens/secrets you need to add to GitHub.

Usage:
    python3 get_tokens.py instagram
    python3 get_tokens.py youtube
    python3 get_tokens.py tiktok

Prerequisites — have these ready before running:
  Instagram : Meta Developer app with instagram_basic, instagram_content_publish
              scopes. App ID and App Secret from developers.facebook.com.
  YouTube   : Google Cloud project with YouTube Data API v3 enabled.
              OAuth 2.0 client credentials (client_id, client_secret).
  TikTok    : TikTok Developer app with video.publish scope approved.
              Client Key and Client Secret from developers.tiktok.com.
"""

import sys
import json
import secrets
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlencode, urlparse, parse_qs

import requests

REDIRECT_URI = "http://localhost:8080/callback"


# ── Instagram ─────────────────────────────────────────────────────────────────

def get_instagram_token():
    """
    Uses the Meta App Dashboard token generator (no redirect URI needed).

    In the dashboard: Instagram → API setup with Instagram login → Step 2 →
    Add account → log in → copy the generated token.
    """
    print("\n=== Instagram Long-Lived Token ===\n")
    app_id = input("Enter your Meta App ID: ").strip()
    app_secret = input("Enter your Meta App Secret: ").strip()

    dashboard_url = f"https://developers.facebook.com/apps/{app_id}/use_cases/customize/API-Setup/?use_case_enum=INSTAGRAM_BUSINESS"
    print(f"\nOpening your Meta App Dashboard...")
    print(f"URL: {dashboard_url}")
    webbrowser.open(dashboard_url)

    print("""
In the dashboard:
  1. Scroll to section 2 "Generate access tokens"
  2. Click "Add account"
  3. Log in with the podcast Instagram account
  4. After it loads back, you'll see the account listed with a "Generate token" button
  5. Click "Generate token" → copy the token shown
""")
    token = input("Paste the token here: ").strip()

    # Dashboard tokens are already long-lived; try exchange anyway, fall back to original
    print("\nValidating token...")
    resp = requests.get(
        "https://graph.instagram.com/access_token",
        params={
            "grant_type": "ig_exchange_token",
            "client_secret": app_secret,
            "access_token": token,
        },
        timeout=15
    )
    long_token = resp.json().get("access_token", token) if resp.ok else token
    if not resp.ok:
        print("  (Token is already long-lived — using as-is)")

    # Get user ID
    resp2 = requests.get(
        "https://graph.instagram.com/v21.0/me",
        params={"fields": "user_id,username", "access_token": long_token},
        timeout=15
    )
    resp2.raise_for_status()
    user_id = resp2.json().get("user_id") or resp2.json().get("id")
    username = resp2.json().get("username", "")

    print(f"\n✓ Success! Account: @{username}\n")
    print("Add these to GitHub Secrets:\n")
    print(f"  INSTAGRAM_USER_ID       = {user_id}")
    print(f"  INSTAGRAM_ACCESS_TOKEN  = {long_token}")
    print("\nNote: The workflow auto-refreshes this token daily.")


# ── YouTube ───────────────────────────────────────────────────────────────────

def get_youtube_token():
    print("\n=== YouTube Refresh Token ===\n")
    client_id = input("Enter your Google OAuth Client ID: ").strip()
    client_secret = input("Enter your Google OAuth Client Secret: ").strip()

    state = secrets.token_urlsafe(16)
    auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth?"
        + urlencode({
            "client_id": client_id,
            "redirect_uri": REDIRECT_URI,
            "response_type": "code",
            "scope": "https://www.googleapis.com/auth/youtube.upload",
            "access_type": "offline",
            "prompt": "consent",
            "state": state,
        })
    )
    print(f"\nOpening browser for Google authorization...")
    print(f"URL: {auth_url}\n")
    webbrowser.open(auth_url)

    code = _capture_callback_code()

    resp = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": REDIRECT_URI,
            "grant_type": "authorization_code",
            "code": code,
        },
        timeout=15
    )
    resp.raise_for_status()
    data = resp.json()

    print("\n✓ Success! Add these to GitHub Secrets:\n")
    print(f"  YOUTUBE_CLIENT_ID      = {client_id}")
    print(f"  YOUTUBE_CLIENT_SECRET  = {client_secret}")
    print(f"  YOUTUBE_REFRESH_TOKEN  = {data['refresh_token']}")


# ── TikTok ────────────────────────────────────────────────────────────────────

def get_tiktok_token():
    print("\n=== TikTok Refresh Token ===\n")
    client_key = input("Enter your TikTok Client Key: ").strip()
    client_secret = input("Enter your TikTok Client Secret: ").strip()

    state = secrets.token_urlsafe(16)
    auth_url = (
        "https://www.tiktok.com/v2/auth/authorize?"
        + urlencode({
            "client_key": client_key,
            "redirect_uri": REDIRECT_URI,
            "response_type": "code",
            "scope": "user.info.basic,video.publish",
            "state": state,
        })
    )
    print(f"\nOpening browser for TikTok authorization...")
    print(f"URL: {auth_url}\n")
    webbrowser.open(auth_url)

    code = _capture_callback_code()

    resp = requests.post(
        "https://open.tiktokapis.com/v2/oauth/token/",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "client_key": client_key,
            "client_secret": client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": REDIRECT_URI,
        },
        timeout=15
    )
    resp.raise_for_status()
    data = resp.json().get("data", resp.json())

    print("\n✓ Success! Add these to GitHub Secrets:\n")
    print(f"  TIKTOK_CLIENT_KEY      = {client_key}")
    print(f"  TIKTOK_CLIENT_SECRET   = {client_secret}")
    print(f"  TIKTOK_REFRESH_TOKEN   = {data['refresh_token']}")
    print("\nNote: TikTok refresh tokens expire after 365 days.")


# ── Local callback server ─────────────────────────────────────────────────────

_captured_code = None

class _CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global _captured_code
        params = parse_qs(urlparse(self.path).query)
        _captured_code = params.get("code", [None])[0]
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"<h2>Authorization complete. You can close this tab.</h2>")

    def log_message(self, *args):
        pass  # silence request logs


def _capture_callback_code():
    print("Waiting for OAuth redirect on http://localhost:8080 ...")
    server = HTTPServer(("localhost", 8080), _CallbackHandler)
    server.handle_request()
    if not _captured_code:
        raise RuntimeError("No authorization code received.")
    print(f"  ✓ Got authorization code.")
    return _captured_code


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ("instagram", "youtube", "tiktok"):
        print("Usage: python3 get_tokens.py [instagram|youtube|tiktok]")
        sys.exit(1)

    platform = sys.argv[1]
    if platform == "instagram":
        get_instagram_token()
    elif platform == "youtube":
        get_youtube_token()
    elif platform == "tiktok":
        get_tiktok_token()
