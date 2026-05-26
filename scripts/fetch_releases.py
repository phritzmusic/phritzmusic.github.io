#!/usr/bin/env python3
"""
fetch_releases.py
─────────────────
Incrementally updates releases from the three phritz Spotify artist pages.

On each run it reads the existing data/releases-spotify.js, then for each
artist fetches only pages newer than the most-recent known release date,
merges the results, and rewrites the file only when something changed.

Full re-fetch behaviour: if the data file is missing or empty, fetches
everything. Otherwise only the first 1-2 pages per artist are needed on
most days (no new releases → single API call per artist, then stops).

Run automatically by the GitHub Action, or locally:
    SPOTIFY_CLIENT_ID=xxx SPOTIFY_CLIENT_SECRET=yyy python3 scripts/fetch_releases.py
"""

import base64
import json
import os
import re
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


# ── Read existing data ────────────────────────────────────────────────────────

def read_existing_releases():
    """
    Parse the existing JS output file and return (releases_list, links_set).
    releases_list: list of dicts with keys title/project/artwork/link/year/release_date
    links_set: set of Spotify album links already in the file
    """
    if not os.path.exists(OUTPUT):
        print("  No existing data file — will do full fetch.")
        return [], set()

    try:
        with open(OUTPUT, "r", encoding="utf-8") as f:
            content = f.read()

        releases = []
        # Each release block looks like:  {  key: "value", ...  }
        for block in re.finditer(r'\{[^{}]+\}', content, re.DOTALL):
            text = block.group()
            r = {}
            for key, val in re.findall(r'(\w+):\s+"([^"]*)"', text):
                r[key] = val
            year_m = re.search(r'year:\s+(\d+)', text)
            if year_m:
                r["year"] = int(year_m.group(1))
            if r.get("link") and r.get("title"):
                releases.append(r)

        links = {r["link"] for r in releases}
        print(f"  Existing data: {len(releases)} releases, "
              f"latest: {max((r.get('release_date','') for r in releases), default='—')}")
        return releases, links

    except Exception as exc:
        print(f"  WARNING: could not parse existing data ({exc}); doing full fetch.",
              file=sys.stderr)
        return [], set()


# ── Spotify helpers ──────────────────────────────────────────────────────────

def get_token(client_id: str, client_secret: str) -> str:
    creds = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    req = Request(
        "https://accounts.spotify.com/api/token",
        data=b"grant_type=client_credentials",
        headers={
            "Authorization": f"Basic {creds}",
            "Content-Type":  "application/x-www-form-urlencoded",
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
            print(f"  Auth OK — token_type={data.get('token_type','?')}, "
                  f"expires_in={data.get('expires_in','?')}s")
            return token
    except HTTPError as e:
        body = e.read().decode(errors="replace")
        sys.exit(
            f"ERROR: Spotify auth failed with HTTP {e.code}.\n"
            f"Response: {body[:500]}\n"
            f"→ Check SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET."
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
                print(f"  Rate-limited (429). Waiting {retry_after}s "
                      f"(attempt {attempt}/{max_retries})…", file=sys.stderr)
                time.sleep(retry_after)
                if attempt == max_retries:
                    raise
            else:
                body = e.read().decode(errors="replace")
                print(f"  HTTP {e.code}: {body[:300]}", file=sys.stderr)
                raise
    return {}


def fetch_new_for_artist(artist_id: str, token: str, known_links: set) -> list:
    """
    Fetch pages for this artist, stopping as soon as a full page contains
    only already-known releases (everything older is definitely known too,
    since Spotify returns newest-first).

    Returns only the genuinely new releases found.
    """
    headers = {"Authorization": f"Bearer {token}"}
    # Omit `limit` — Spotify's /v1/artists/{id}/albums now rejects explicit
    # limit values with a misleading 400 "Invalid limit" error.
    url = (
        f"https://api.spotify.com/v1/artists/{artist_id}/albums"
        f"?include_groups=album,single"
    )
    new_releases = []
    page = 0

    while url:
        page += 1
        try:
            data = fetch_url_with_retry(url, headers)
        except HTTPError as e:
            print(f"  Giving up on page {page} (HTTP {e.code}).", file=sys.stderr)
            break
        except Exception as e:
            print(f"  Unexpected error on page {page}: {e}", file=sys.stderr)
            break

        items = data.get("items") or []
        found_new_on_page = False

        for item in items:
            link = item["external_urls"]["spotify"]
            if link in known_links:
                continue  # already have this one
            found_new_on_page = True
            images = item.get("images", [])
            new_releases.append({
                "title":        item["name"],
                "artwork":      images[0]["url"] if images else "",
                "link":         link,
                "year":         int(item["release_date"][:4]),
                "release_date": item["release_date"],
            })

        total = data.get("total", "?")
        print(f"  page {page}: {len(items)} items (API total: {total}), "
              f"{sum(1 for i in items if i['external_urls']['spotify'] not in known_links)} new")

        if not found_new_on_page:
            # Entire page was already known → nothing older will be new either
            break

        url = data.get("next")

    return new_releases


# ── JS output builder ─────────────────────────────────────────────────────────

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


def write_output(releases: list) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    body = ",\n".join(js_entry(r) for r in releases)
    content = f"""\
/* AUTO-GENERATED by scripts/fetch_releases.py — do not edit manually.
 * Last updated: {now}
 * Source:       Spotify Web API (Client Credentials)
 *
 * Incremental: only new releases are fetched on each run; existing data
 * is preserved and merged. For collabs not on your Spotify pages, use
 * releases-manual.js instead.
 */

window.RELEASES_SPOTIFY = [
{body}
];
"""
    os.makedirs("data", exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"\nWritten → {OUTPUT}  ({len(releases)} total releases)")


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    client_id     = os.environ.get("SPOTIFY_CLIENT_ID",     "").strip()
    client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET", "").strip()

    if not client_id or not client_secret:
        sys.exit(
            "ERROR: SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET must be set.\n"
            f"  SPOTIFY_CLIENT_ID     is {'set' if client_id else 'MISSING'}\n"
            f"  SPOTIFY_CLIENT_SECRET is {'set' if client_secret else 'MISSING'}\n"
            "Add them as GitHub Secrets under Settings → Secrets → Actions."
        )

    print(f"SPOTIFY_CLIENT_ID     : {'*' * (len(client_id) - 4) + client_id[-4:]}")
    print(f"SPOTIFY_CLIENT_SECRET : {'*' * (len(client_secret) - 4) + client_secret[-4:]}")

    # ── Load what we already have ────────────────────────────────────────────
    print("\nReading existing data…")
    existing_releases, known_links = read_existing_releases()

    # ── Auth ─────────────────────────────────────────────────────────────────
    print("\nAuthenticating with Spotify…")
    token = get_token(client_id, client_secret)

    # ── Fetch only what's new ────────────────────────────────────────────────
    all_new: list[dict] = []
    seen_new: set[str] = set()

    for project, artist_id in ARTISTS.items():
        print(f"\nChecking '{project}' (ID: {artist_id}) for new releases…")
        new = fetch_new_for_artist(artist_id, token, known_links)
        print(f"  → {len(new)} new release(s) for {project}")
        time.sleep(1)  # small pause between artists
        for r in new:
            if r["link"] not in seen_new:
                seen_new.add(r["link"])
                all_new.append({"project": project, **r})

    # ── Merge + sort ──────────────────────────────────────────────────────────
    if not all_new:
        print("\nNo new releases found — data is already up to date.")
        return  # exit 0; workflow will skip the commit step (no diff)

    print(f"\n{len(all_new)} new release(s) found across all artists.")

    # Combine and deduplicate (new takes precedence over existing for same link)
    merged_links: set[str] = set()
    merged: list[dict] = []
    for r in all_new + existing_releases:
        if r["link"] not in merged_links:
            merged_links.add(r["link"])
            merged.append(r)

    merged.sort(key=lambda r: r.get("release_date", ""), reverse=True)
    print(f"Total after merge: {len(merged)} releases")

    write_output(merged)


if __name__ == "__main__":
    main()
