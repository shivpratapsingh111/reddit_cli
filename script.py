import requests
import time
import re
from bs4 import BeautifulSoup

import config


BASE_URL = "https://www.reddit.com"


def log(msg, level="INFO"):
    ts = time.strftime("%H:%M:%S")
    print(f"[{ts}] [{level}] {msg}")


def build_session():
    session = requests.Session()

    ua = config.random_user_agent()
    log(f"Using User-Agent: {ua}", "INIT")

    session.headers.update({
        "user-agent": ua,
        "accept": "*/*",
        "referer": f"{BASE_URL}/user/{config.USERNAME}/comments/",
        "origin": BASE_URL,
    })

    for pair in config.COOKIES_RAW.strip().split(";"):
        if "=" in pair:
            k, v = pair.strip().split("=", 1)
            session.cookies.set(k, v)

    return session


def get_csrf_token(session):
    token = session.cookies.get("csrf_token")
    if not token:
        raise RuntimeError("csrf_token cookie not found (not logged in?)")
    log("CSRF token loaded", "AUTH")
    return token


def extract_comment_ids(html):
    soup = BeautifulSoup(html, "html.parser")
    ids = set()

    for tag in soup.select("shreddit-profile-comment[comment-id]"):
        cid = tag.get("comment-id")
        if cid and cid.startswith("t1_"):
            ids.add(cid)

    return ids


def extract_next_after(html):
    match = re.search(r'after=([A-Za-z0-9_%]+)', html)
    return match.group(1) if match else None


def fetch_initial_comments(session):
    url = f"{BASE_URL}/user/{config.USERNAME}/comments/"
    log("Fetching initial comments page", "FETCH")
    r = session.get(url)
    r.raise_for_status()
    return r.text


def fetch_more_comments(session, after):
    url = f"{BASE_URL}/svc/shreddit/profiles/profile_comments-more-posts/new/"
    params = {
        "after": after,
        "name": config.USERNAME,
        "feedLength": 100
    }

    log(f"Fetching more comments (after={after})", "FETCH")
    r = session.get(url, params=params)
    r.raise_for_status()
    return r.text


def delete_comment(session, csrf_token, comment_id):
    url = f"{BASE_URL}/svc/shreddit/graphql"

    payload = {
        "operation": "DeleteComment",
        "variables": {
            "input": {
                "commentId": comment_id
            }
        },
        "csrf_token": csrf_token
    }

    r = session.post(url, json=payload)
    r.raise_for_status()
    data = r.json()

    return data.get("data", {}).get("deleteComment", {}).get("ok") is True

def fetch_all_visible_comments(session):
    all_comment_ids = set()
    seen_afters = set()

    html = fetch_initial_comments(session)
    found = extract_comment_ids(html)
    all_comment_ids |= found

    after = extract_next_after(html)

    while after:
        if after in seen_afters:
            break

        seen_afters.add(after)
        time.sleep(config.PAGE_DELAY)

        html = fetch_more_comments(session, after)
        found = extract_comment_ids(html)
        new_ids = found - all_comment_ids

        if not new_ids:
            break

        all_comment_ids |= new_ids
        next_after = extract_next_after(html)

        if not next_after or next_after == after:
            break

        after = next_after

    return all_comment_ids


def main():
    log("Starting Reddit comment wipe", "START")

    session = build_session()
    csrf_token = get_csrf_token(session)
    errors = 0
    total_deleted = 0
    round_num = 1

    while True:
        log(f"=== WIPE ROUND {round_num} ===", "ROUND")

        comment_ids = fetch_all_visible_comments(session)

        if not comment_ids:
            log("No comments remaining. Account is clean 🎉", "DONE")
            break

        log(f"Found {len(comment_ids)} comments to delete", "SUMMARY")

        for idx, cid in enumerate(sorted(comment_ids), 1):
            log(f"({idx}/{len(comment_ids)}) Deleting {cid}", "DELETE")
            try:
                ok = delete_comment(session, csrf_token, cid)
                if ok:
                    total_deleted += 1
                    log(f"{cid} deleted", "OK")
                else:
                    log(f"{cid} delete failed", "FAIL")
                    errors += 1
            except Exception as e:
                log(f"{cid} error: {e}", "ERROR")
                errors += 1

            if errors >= config.MAX_DELETE_ERRORS:
                log("Too many errors, aborting", "ABORT")
                return

            time.sleep(config.random_delete_delay())

        round_num += 1
        time.sleep(3)  # let Reddit refresh feed state

    log(f"TOTAL COMMENTS DELETED: {total_deleted}", "SUMMARY")


if __name__ == "__main__":
    main()
