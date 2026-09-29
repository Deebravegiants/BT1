#!/usr/bin/env python3
"""
Fetch every validated_questions report via DeepWiki's JSON API - no browser.

Instead of driving Selenium to a /search/ page and clicking "Copy response",
this hits the endpoint the page itself calls:

    GET https://api.devin.ai/ada/query/<full-slug>

where <full-slug> is the entire path segment after /search/ (the text prefix
AND the uuid - the bare uuid returns 404). The response markdown is rebuilt
from the `chunk` events that sit OUTSIDE any thoughts_start/thoughts_end pair,
which yields exactly what the Copy button puts on the clipboard.

Plain requests/httpx/curl always get "429 Vercel Security Checkpoint" - the
block is on the TLS/HTTP2 fingerprint, not on headers or cookies - so this
uses curl_cffi's Chrome impersonation.

Requires one dependency:

    pip install curl_cffi

Usage:
    python run_validator_report_fast.py                 # all pending, 32 workers
    python run_validator_report_fast.py -c 64           # more concurrency
    python run_validator_report_fast.py --limit 200     # try a small batch first
    python run_validator_report_fast.py --retry-failed
    python run_validator_report_fast.py --keep-thoughts # include reasoning text
"""
import argparse
import json
import os
import random
import re
import sys
import threading
import time
import uuid
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import quote, urlsplit

try:
    from curl_cffi import requests as creq
except ImportError:
    sys.exit("curl_cffi is required:  pip install curl_cffi")

PROJECT_ROOT = Path(__file__).resolve().parent
VALIDATED_QUESTIONS_DIR = PROJECT_ROOT / os.environ.get("VALIDATED_QUESTIONS_DIR", "validated_questions")
VALIDATED_DIR = PROJECT_ROOT / os.environ.get("VALIDATED_DIR", "validated")
PROGRESS_FILE = PROJECT_ROOT / "validated_report_fast_progress.json"

API_BASE = "https://api.devin.ai/ada/query/"
IMPERSONATE = os.environ.get("CURL_IMPERSONATE", "chrome131")
HEADERS = {
    "accept": "application/json",
    "origin": "https://deepwiki.com",
    "referer": "https://deepwiki.com/",
    "accept-language": "en",
}

# Same rejection markers the Selenium version used.
REJECT_MARKERS = ("NoVulnerability", "I cannot perform this security")

_local = threading.local()
_lock = threading.Lock()
_stop = threading.Event()


def session():
    """One curl_cffi session per thread (sessions are not thread-safe)."""
    s = getattr(_local, "s", None)
    if s is None:
        s = creq.Session(impersonate=IMPERSONATE, headers=HEADERS, timeout=90)
        _local.s = s
    return s


def slug_of(url):
    """The /search/<slug> segment, which is the API's query_id."""
    m = re.search(r"/search/([^?#]+)", urlsplit(url).path + "?" + (urlsplit(url).query or ""))
    if not m:
        m = re.search(r"/search/([^?#]+)", url)
    return m.group(1) if m else None


def collect_targets():
    """[(url, slug)] for every unique /search/ URL in validated_questions/."""
    if not VALIDATED_QUESTIONS_DIR.exists():
        print(f"Directory {VALIDATED_QUESTIONS_DIR} does not exist")
        return []

    seen, out, skipped = set(), [], 0
    for jf in sorted(VALIDATED_QUESTIONS_DIR.glob("*.json")):
        try:
            data = json.loads(jf.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"Error reading {jf.name}: {e}")
            continue
        for it in (data if isinstance(data, list) else [data]):
            if not isinstance(it, dict):
                continue
            url = it.get("url")
            if not isinstance(url, str) or not url.strip() or url in seen:
                continue
            seen.add(url)
            slug = slug_of(url)
            if slug:
                out.append((url, slug))
            else:
                skipped += 1
    if skipped:
        print(f"Skipped {skipped} non-/search/ URLs (no query id to fetch)")
    return out


def extract_markdown(payload, keep_thoughts=False):
    """
    Rebuild the answer markdown from the query payload.

    `response` is an ordered event list. Text lives in `chunk` events, but the
    model's reasoning is also delivered as `chunk`s, fenced by thoughts_start /
    thoughts_end. Only chunks at thoughts-depth 0 are the real answer.
    """
    queries = payload.get("queries") or []
    if not queries:
        return None, "no queries"

    q = queries[-1]
    state = q.get("state")
    events = q.get("response") or []
    if not events:
        return None, f"empty response (state={state})"

    depth, answer, thoughts = 0, [], []
    for ev in events:
        if not isinstance(ev, dict):
            continue
        t = ev.get("type")
        if t == "thoughts_start":
            depth += 1
        elif t == "thoughts_end":
            depth = max(0, depth - 1)
        elif t == "chunk":
            (thoughts if depth > 0 else answer).append(ev.get("data", ""))

    md = "".join(answer).strip()
    if keep_thoughts and thoughts:
        md = md + "\n\n---\n\n## Reasoning\n\n" + "".join(thoughts).strip()
    if not md:
        return None, f"no answer text (state={state})"
    if state == "pending":
        return None, "still pending"
    return md, None


def fetch(slug, tries=4):
    """GET the query, retrying on rate limit / transport errors."""
    url = API_BASE + quote(slug, safe="")
    last = "unknown"
    for attempt in range(tries):
        if _stop.is_set():
            return None, "aborted"
        try:
            r = session().get(url)
        except Exception as e:
            last = f"{type(e).__name__}: {e}"
        else:
            if r.status_code == 200:
                try:
                    return r.json(), None
                except Exception as e:
                    return None, f"bad json: {e}"
            if r.status_code == 404:
                return None, "404 query not found"
            last = f"http {r.status_code}"
            if r.status_code in (403, 429) or r.status_code >= 500:
                # Vercel checkpoint or throttle: back off, then retry.
                time.sleep((2 ** attempt) + random.random() * 1.5)
                continue
            return None, last
        time.sleep((2 ** attempt) * 0.5 + random.random())
    return None, last


def load_progress():
    if not PROGRESS_FILE.exists():
        return {"done": {}, "failed": {}, "empty": {}, "missing": {}}
    try:
        d = json.loads(PROGRESS_FILE.read_text(encoding="utf-8") or "{}")
    except Exception as e:
        print(f"Could not read {PROGRESS_FILE.name} ({e}), starting fresh")
        return {"done": {}, "failed": {}, "empty": {}, "missing": {}}
    return {k: (d.get(k) if isinstance(d.get(k), dict) else {})
            for k in ("done", "failed", "empty", "missing")}


def save_progress(p):
    tmp = PROGRESS_FILE.with_suffix(".json.tmp")
    try:
        tmp.write_text(json.dumps(p, indent=2, ensure_ascii=False), encoding="utf-8")
        tmp.replace(PROGRESS_FILE)
    except Exception as e:
        print(f"Error saving progress: {e}")


def main():
    ap = argparse.ArgumentParser(description="Fetch validated reports via the DeepWiki JSON API")
    ap.add_argument("-c", "--concurrency", type=int, default=62, help="parallel requests (default 32)")
    ap.add_argument("--limit", type=int, default=0, help="stop after N URLs (0 = all)")
    ap.add_argument("--retry-failed", action="store_true", help="also retry previously failed URLs")
    ap.add_argument("--restart", action="store_true", help="ignore existing progress")
    ap.add_argument("--keep-thoughts", action="store_true", help="append the model's reasoning to each report")
    args = ap.parse_args()

    VALIDATED_DIR.mkdir(exist_ok=True)

    targets = collect_targets()
    if not targets:
        print("No URLs found in validated_questions/")
        return 0

    progress = ({"done": {}, "failed": {}, "empty": {}, "missing": {}}
                if args.restart else load_progress())
    done, failed = progress["done"], progress["failed"]
    empty, missing = progress["empty"], progress["missing"]

    # `missing` is a server-side 404: the query no longer exists, so retrying
    # it can never succeed. Those are excluded permanently, even with
    # --retry-failed, unless --restart wipes the progress file.
    pending = [
        (u, s) for (u, s) in targets
        if u not in done and u not in empty and u not in missing
        and (args.retry_failed or u not in failed)
    ]
    if args.limit:
        pending = pending[:args.limit]

    print(f"Unique URLs      : {len(targets)}")
    print(f"Already done     : {len(done)}   no-vuln: {len(empty)}   "
          f"gone (404): {len(missing)}   failed: {len(failed)}")
    print(f"To fetch now     : {len(pending)}  (concurrency {args.concurrency})\n")
    if not pending:
        print("Nothing left to process.")
        return 0

    stats = {"saved": 0, "novuln": 0, "failed": 0, "missing": 0}
    started = time.time()
    completed = 0

    def work(item):
        url, slug = item
        payload, err = fetch(slug)
        if err:
            return url, None, err
        md, err = extract_markdown(payload, keep_thoughts=args.keep_thoughts)
        if err:
            return url, None, err
        if any(m in md for m in REJECT_MARKERS):
            return url, "", None          # reached, but nothing to keep
        return url, md, None

    pool = ThreadPoolExecutor(max_workers=args.concurrency)
    try:
        futures = {pool.submit(work, it): it for it in pending}
        for fut in as_completed(futures):
                url, md, err = fut.result()
                with _lock:
                    if err == "404 query not found":
                        missing[url] = str(datetime.now())
                        failed.pop(url, None)
                        stats["missing"] += 1
                    elif err:
                        failed[url] = err
                        stats["failed"] += 1
                    elif md == "":
                        empty[url] = str(datetime.now())
                        failed.pop(url, None)
                        stats["novuln"] += 1
                    else:
                        name = VALIDATED_DIR / f"audit_{uuid.uuid4().hex}.md"
                        name.write_text(md, encoding="utf-8")
                        done[url] = name.name
                        failed.pop(url, None)
                        stats["saved"] += 1

                    completed += 1
                    if completed % 50 == 0:
                        save_progress(progress)
                    if completed % 50 == 0 or completed == len(pending):
                        el = time.time() - started
                        rate = completed / el if el else 0
                        eta = (len(pending) - completed) / rate / 60 if rate else 0
                        print(f"[{completed}/{len(pending)}] saved={stats['saved']} "
                              f"no-vuln={stats['novuln']} gone={stats['missing']} "
                              f"failed={stats['failed']} | {rate:.1f}/s | ETA {eta:.1f} min")
    except KeyboardInterrupt:
        print("\nInterrupting - cancelling queued work...")
    finally:
        # Tell in-flight fetches to bail, drop everything still queued, and do
        # not wait around. Anything not recorded below is simply retried on the
        # next run, so stopping here is always safe.
        _stop.set()
        pool.shutdown(wait=False, cancel_futures=True)
        save_progress(progress)

    el = time.time() - started
    print("\n=== Summary ===")
    print(f"Fetched        : {completed}/{len(pending)}")
    print(f"Reports saved  : {stats['saved']}  -> {VALIDATED_DIR.name}/")
    print(f"No-vulnerability: {stats['novuln']}")
    print(f"Gone (404)     : {stats['missing']}")
    print(f"Failed (retryable): {stats['failed']}")
    print(f"Elapsed        : {el/60:.1f} min ({completed/el:.1f}/s)" if el else "")
    print(f"validated/ now holds {len(list(VALIDATED_DIR.glob('*.md')))} files")
    print(f"Progress file  : {PROGRESS_FILE.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
