#!/usr/bin/env python3
"""
fetch_releases.py
─────────────────
Fetches all releases from the three phritz Spotify artist pages and writes
data/releases-spotify.js. Run automatically by the GitHub Action, or locally:

    SPOTIFY_CLIENT_ID=xxx SPOTIFY_CLIENT_SECRET=yyy python3 scripts/fetch_releases.py

Get free API credentials at https://developer.spotify.com/dashboard
(Create App → note Client ID + Client Secret → add as GitHub Secrets)
"""

import base64
import json
import os
import sys
import time
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.error import HTTPError

# ── Artist pages to fetch ────────────────────────────────────────────────────
ARTISTS = {
    "phritz":               "4pVTHC0fGP57HJ7Wy6cbtt",
    "tai hirose":           "6wA6or5a0wvssdsKKQK03j",
    "tiny pool centennial": "7uA6zWZn3RS6XkkhBeVcDD",
}

OUTPUT = "data/releases-spotify.js"


# ── Spotify helpers ──────────────────────────────────────────────────────────

def get_token(client_id: str, client_secret: str) -> str:
    creds = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    req = Request(
        "https://accounts.spotify.com/api/token",
        data=b"grant_type=client_credentials",
        headers={
            "Authorization": f"Basic {creds}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )
    try:
        with urlopen(req) as r:
            body = r.read()
            data = json.loads(body)
            token = data.get("access_token")
            if not token:
                sys.exit(
                    f"ERROR: Spotify auth response contained no access_token.\n"
                    f"Response: {body.decode()[:500]}"
                )
            token_type = data.get("token_type", "?")
            expires_in = data.get("expires_in", "?")
            print(f"  Auth OK — token_type={token_type}, expires_in={expires_in}s")
            return token
    except HTTPError as e:
        body = e.read().decode(errors="replace")
        sys.exit(
            f"ERROR: Spotify auth failed with HTTP {e.code}.\n"
            f"Response: {body[:500]}\n"
            f"→ Check that SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET are correct."
        )
    except Exception as e:
        sys.exit(f"ERROR: Unexpected error during Spotify auth: {e}")


def fetch_url_with_retry(url: str, headers: dict, max_retries: int = 6) -> dict:
    """Fetch a URL, retrying on 429 (rate limit) with Retry-After back-off."""
    for attempt in range(1, max_retries + 1):
        req = Request(url, headers=headers)
        try:
            with urlopen(req) as r:
                return json.loads(r.read())
        except HTTPError as e:
            if e.code == 429:
                retry_after = int(e.headers.get("Retry-After", 60))
                print(
                    f"  Rate-limited (429). Waiting {retry_after}s "
                    f"(attempt {attempt}/{max_retries})…",
                    file=sys.stderr,
                )
                time.sleep(retry_after)
                if attempt == max_retries:
                    raise  # give up after final retry
            else:
                body = e.read().decode(errors="replace")
                print(f"  HTTP {e.code}: {body[:300]}", file=sys.stderr)
                raise
    return {}  # unreachable, but keeps type checkers happy


def fetch_artist_releases(artist_id: str, token: str) -> list[dict]:
    """Returns all albums + singles for the given artist (handles pagination)."""
    headers = {"Authorization": f"Bearer {token}"}
    url = (
        f"https://api.spotify.com/v1/artists/{artist_id}/albums"
        f"?include_groups=album,single&limit=20"
    )
    results = []
    page = 0
    while url:
        page += 1
        try:
            data = fetch_url_with_retry(url, headers)
        except HTTPError as e:
            print(f"  Giving up on page {page} after repeated errors (HTTP {e.code}).", file=sys.stderr)
            break
        except Exception as e:
            print(f"  Unexpected error on page {page}: {e}", file=sys.stderr)
            break

        total = data.get("total", "?")
        items = data.get("items") or []
        print(f"  page {page}: {len(items)} items (API total: {total})")

        for item in items:
            images = item.get("images", [])
            results.append({
                "title":        item["name"],
                "artwork":      images[0]["url"] if images else "",
                "link":         item["external_urls"]["spotify"],
                "year":         int(item["release_date"][:4]),
                "release_date": item["release_date"],
            })
        url = data.get("next")  # None on last page
    return results


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    client_id     = os.environ.get("SPOTIFY_CLIENT_ID", "").strip()
    client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET", "").strip()

    if not client_id or not client_secret:
        sys.exit(
            "ERROR: SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET must be set.\n"
            f"  SPOTIFY_CLIENT_ID     is {'set' if client_id else 'MISSING or empty'}\n"
            f"  SPOTIFY_CLIENT_SECRET is {'set' if client_secret else 'MISSING or empty'}\n"
            "Get credentials at https://developer.spotify.com/dashboard\n"
            "Add them as GitHub Secrets under Settings → Secrets → Actions."
        )

    print(f"SPOTIFY_CLIENT_ID     : {'*' * (len(client_id) - 4) + client_id[-4:]}")
    print(f"SPOTIFY_CLIENT_SECRET : {'*' * (len(client_secret) - 4) + client_secret[-4:]}")
    print("Authenticating with Spotify…")
    token = get_token(client_id, client_secret)

    all_releases: list[dict] = []
    seen_links: set[str] = set()

    for project, artist_id in ARTISTS.items():
        print(f"\nFetching releases for '{project}' (ID: {artist_id})…")
        releases = fetch_artist_releases(artist_id, token)
        print(f"  → {len(releases)} releases returned for {project}")
        time.sleep(1)  # small pause between artists to stay within rate limits
        for r in releases:
            if r["link"] in seen_links:
                print(f"    skip duplicate: {r['title']}")
                continue
            seen_links.add(r["link"])
            all_releases.append({"project": project, **r})

    # Newest first
    all_releases.sort(key=lambda r: r["release_date"], reverse=True)
    print(f"\nTotal unique releases across all artists: {len(all_releases)}")

    if len(all_releases) == 0:
        print(
            "\nWARNING: 0 releases found — skipping file write to preserve existing data.",
            file=sys.stderr,
        )
        sys.exit(1)  # non-zero exit → prevents the commit step from running

    # ── Build JS output ──────────────────────────────────────────────────────
    def js_entry(r: dict) -> str:
        return (
            "  {\n"
            f"    title:        {json.dumps(r['title'])},\n"
            f"    project:      {json.dumps(r['project'])},\n"
            f"    artwork:      {json.dumps(r['artwork'])},\n"
            f"    link:         {json.dumps(r['link'])},\n"
            f"    year:         {r['year']},\n"
            f"    release_date: {json.dumps(r['release_date'])}\n"
            "  }"
        )

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    body = ",\n".join(js_entry(r) for r in all_releases)

    content = f"""\
/* AUTO-GENERATED by scripts/fetch_releases.py — do not edit manually.
 * Last updated: {now}
 * Source:       Spotify Web API (Client Credentials)
 *
 * This file is rewritten each time the GitHub Action runs (daily + on push).
 * For collabs/features not on your primary Spotify pages, use releases-manual.js
 */

window.RELEASES_SPOTIFY = [
{body}
];
"""

    os.makedirs("data", exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"\nWritten → {OUTPUT}")


if __name__ == "__main__":
    main()
