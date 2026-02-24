#!/usr/bin/env python3
import re
import urllib.request
import sys

PLAYLIST_FILE = "playlist.m3u"          # Path to your M3U file
COOKIE_URL = "https://jtv.pfy.workers.dev"  # Endpoint that returns the new cookie value

def fetch_new_cookie():
    """Fetch the new cookie string from the given URL."""
    try:
        with urllib.request.urlopen(COOKIE_URL) as response:
            # Assume the response is plain text containing the full __hdnea__ value
            # e.g. "st=123...~exp=456...~acl=/*~hmac=abc..."
            new_cookie = response.read().decode('utf-8').strip()
            if not new_cookie:
                raise ValueError("Empty response from cookie URL")
            return new_cookie
    except Exception as e:
        print(f"Error fetching new cookie: {e}")
        sys.exit(1)

def update_playlist(old_content, new_cookie):
    """
    Replace all occurrences of __hdnea__=<old_value> with __hdnea__=<new_cookie>
    in both the #EXTHTTP line and the stream URLs.
    """
    # Pattern to find __hdnea__=... up to the next &, ", or whitespace
    pattern = r'(__hdnea__=)([^&\"\s]+)'

    def replacer(match):
        return match.group(1) + new_cookie

    new_content = re.sub(pattern, replacer, old_content)
    return new_content

def main():
    print("Fetching new cookie...")
    new_cookie = fetch_new_cookie()
    print(f"New cookie value: {new_cookie[:50]}...")  # Truncate for logging

    print(f"Reading {PLAYLIST_FILE}...")
    try:
        with open(PLAYLIST_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: {PLAYLIST_FILE} not found.")
        sys.exit(1)

    updated = update_playlist(content, new_cookie)

    if updated == content:
        print("No changes needed (cookie already matches?).")
        sys.exit(0)

    print("Changes detected. Writing updated playlist...")
    with open(PLAYLIST_FILE, 'w', encoding='utf-8') as f:
        f.write(updated)

    print("Playlist updated successfully.")

if __name__ == "__main__":
    main()
