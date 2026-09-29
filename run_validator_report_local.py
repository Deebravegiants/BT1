#!/usr/bin/env python3
"""
Run every pending validated_questions URL locally, in one go.

Unlike run_validator_report.py (which works off a CI-populated
validation_pending folder, 20 files at a time), this script reads every JSON
file in validated_questions/, collects all URLs, and generates the reports for
all of them into validated/ using a single browser session.

Progress is stored in validated_report_progress.json, so the script can be
stopped at any time (Ctrl+C) and re-run: already-processed URLs are skipped.
Nothing in validated_questions/ is moved, renamed or deleted.

    python run_validator_report_local.py
    python run_validator_report_local.py --limit 100      # stop after 100 URLs
    python run_validator_report_local.py --retry-failed   # re-attempt failures
    python run_validator_report_local.py --headless       # no visible browser
"""
import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

VALIDATED_QUESTIONS_DIR = PROJECT_ROOT / os.environ.get("VALIDATED_QUESTIONS_DIR", "validated_questions")
VALIDATED_DIR = PROJECT_ROOT / os.environ.get("VALIDATED_DIR", "validated")
PROGRESS_FILE = PROJECT_ROOT / "validated_report_progress.json"


def collect_urls():
    """Every url in every JSON file under validated_questions/, de-duplicated."""
    if not VALIDATED_QUESTIONS_DIR.exists():
        print(f"Directory {VALIDATED_QUESTIONS_DIR} does not exist")
        return []

    seen = set()
    urls = []

    for json_file in sorted(VALIDATED_QUESTIONS_DIR.glob("*.json")):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error parsing {json_file.name}: {e}")
            continue
        except Exception as e:
            print(f"Error reading {json_file.name}: {e}")
            continue

        items = data if isinstance(data, list) else [data]
        for item in items:
            if not isinstance(item, dict):
                continue
            url = item.get("url")
            if isinstance(url, str) and url.strip() and url not in seen:
                seen.add(url)
                urls.append(url)

    return urls


def load_progress():
    """{"done": {url: timestamp}, "failed": {url: error}}"""
    if not PROGRESS_FILE.exists():
        return {"done": {}, "failed": {}}

    try:
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            data = json.loads(content) if content else {}
    except (json.JSONDecodeError, OSError) as e:
        print(f"Could not read {PROGRESS_FILE.name} ({e}), starting fresh")
        return {"done": {}, "failed": {}}

    return {
        "done": data.get("done", {}) if isinstance(data.get("done"), dict) else {},
        "failed": data.get("failed", {}) if isinstance(data.get("failed"), dict) else {},
    }


def save_progress(progress):
    tmp = PROGRESS_FILE.with_suffix(".json.tmp")
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(progress, f, indent=2, ensure_ascii=False)
        tmp.replace(PROGRESS_FILE)
    except Exception as e:
        print(f"Error saving progress: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate validated reports for every URL in validated_questions/"
    )
    parser.add_argument("--limit", type=int, default=0,
                        help="stop after this many URLs (0 = no limit)")
    parser.add_argument("--retry-failed", action="store_true",
                        help="also retry URLs that previously failed")
    parser.add_argument("--headless", action="store_true",
                        help="run Chrome headless (clipboard copy may not work)")
    parser.add_argument("--restart", action="store_true",
                        help="ignore existing progress and process every URL again")
    args = parser.parse_args()

    os.environ["CHROME_HEADLESS"] = "true" if args.headless else "false"

    # Imported after CHROME_HEADLESS is set; get_report() writes into validated/.
    from audit_validation import GetValidatedReports

    VALIDATED_DIR.mkdir(exist_ok=True)

    all_urls = collect_urls()
    if not all_urls:
        print("No URLs found in validated_questions/")
        return 0

    progress = {"done": {}, "failed": {}} if args.restart else load_progress()

    pending = [
        u for u in all_urls
        if u not in progress["done"] and (args.retry_failed or u not in progress["failed"])
    ]

    print(f"Found {len(all_urls)} unique URLs in {VALIDATED_QUESTIONS_DIR.name}/")
    print(f"Already done: {len(progress['done'])}  |  previously failed: {len(progress['failed'])}")

    if args.limit and args.limit < len(pending):
        pending = pending[:args.limit]

    total = len(pending)
    if total == 0:
        print("Nothing left to process.")
        return 0

    print(f"Processing {total} URLs -> {VALIDATED_DIR.name}/\n")

    before = len(list(VALIDATED_DIR.glob("*.md")))
    started = time.time()
    report = None
    processed = 0

    try:
        report = GetValidatedReports(teardown=True)

        for i, url in enumerate(pending, 1):
            print(f"[{i}/{total}] {url}")
            try:
                report.get_report(url)
                progress["done"][url] = str(datetime.now())
                progress["failed"].pop(url, None)
            except KeyboardInterrupt:
                raise
            except Exception as e:
                print(f"  failed: {e}")
                progress["failed"][url] = str(e)

            processed += 1
            if processed % 10 == 0:
                save_progress(progress)

    except KeyboardInterrupt:
        print("\nInterrupted - progress saved, re-run to continue.")
    except Exception as e:
        print(f"\n!!! ERROR: {e}")
    finally:
        save_progress(progress)
        if report is not None:
            try:
                report.driver.quit()
            except Exception:
                pass

    after = len(list(VALIDATED_DIR.glob("*.md")))
    elapsed = time.time() - started

    print("\n=== Summary ===")
    print(f"URLs attempted : {processed}/{total}")
    print(f"Succeeded      : {len(progress['done'])} total")
    print(f"Failed         : {len(progress['failed'])} total")
    print(f"New reports    : {after - before} (validated/ now holds {after})")
    print(f"Elapsed        : {elapsed / 60:.1f} min")
    print(f"Progress file  : {PROGRESS_FILE.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
