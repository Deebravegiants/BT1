"""Same job as run_scanner.py, but asks DeepWiki through its MCP API instead of a Selenium browser."""
import json
import os
import time
import uuid
from datetime import datetime
from pathlib import Path

from decouple import config

from deepwiki_mcp import ask_wiki_question, extract_search_url, repo_from_url
from questions import BASE_URL, audit_format, scan_format, validation_format

MAX_RUNTIME_SECONDS = 20 * 60
MAX_FILES_PER_RUN = 30
DELAY_BETWEEN_QUESTIONS = 5  # seconds, to go easy on the free API
VALIDATED_DIR = "validated"


def get_audits_reports():
    return sorted(Path("validated_questions_pending").glob("*.md"))


def get_validated_path():
    return config("VALIDATED_QUESTIONS_PATH", default="validated.json")


def load_processed_reports():
    path = get_validated_path()
    if not os.path.exists(path):
        return set()
    try:
        with open(path, "r") as f:
            content = f.read().strip()
            data = json.loads(content) if content else []
        return {item.get("filename", "") for item in data if "filename" in item}
    except Exception as e:
        print(f"Error loading {path}: {e}")
        return set()


def format_question(filename, content):
    base_filename = Path(filename).name.lower()
    if base_filename.startswith("audit"):
        return scan_format(content)
    if base_filename.startswith("validation"):
        return validation_format(content)
    return audit_format(content)


def save_answer(answer):
    """Save answers that report a vulnerability, same filter as GetValidatedReports.get_report."""
    if not answer or "NoVulnerability" in answer or "I cannot perform this security" in answer:
        return None
    os.makedirs(VALIDATED_DIR, exist_ok=True)
    answer_file = f"{VALIDATED_DIR}/audit_{uuid.uuid4().hex}.md"
    with open(answer_file, "w", encoding="utf-8") as f:
        f.write(answer)
    return answer_file


def save_to_validated(filename, search_url, answer_file):
    """Record the file as processed. No 'url' key, so the browser report step won't try to open it."""
    path = get_validated_path()
    try:
        if os.path.exists(path):
            with open(path, "r") as f:
                content = f.read().strip()
                data = json.loads(content) if content else []
        else:
            data = []
    except json.JSONDecodeError:
        print(f"Invalid {path}, creating new file")
        data = []

    data.append({
        "filename": filename,
        "deepwiki_url": search_url,
        "answer_file": answer_file,
        "source": "mcp",
        "timestamp": str(datetime.now()),
        "report_generated": True,
    })

    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def main():
    start = time.monotonic()
    repo_name = os.environ.get("DEEPWIKI_REPO") or repo_from_url(BASE_URL)

    audit_files = get_audits_reports()
    total = len(audit_files)
    processed_files = load_processed_reports()

    print(f"Repo: {repo_name}")
    print(f"Found {total} audit files to process")
    print(f"Already processed: {len(processed_files)}")

    processed_count = skipped_count = failed_count = found_count = 0

    for i, audit_file in enumerate(audit_files, 1):
        if time.monotonic() - start > MAX_RUNTIME_SECONDS:
            print("\n20-minute limit reached, stopping.")
            break
        if processed_count >= MAX_FILES_PER_RUN:
            break

        if audit_file.name in processed_files:
            print(f"[{i}/{total}] Skipping (already processed): {audit_file.name}")
            skipped_count += 1
            continue

        print(f"\n[{i}/{total}] Processing: {audit_file.name}")

        try:
            content = audit_file.read_text(encoding="utf-8")
            question = format_question(audit_file.name, content)

            asked_at = time.monotonic()
            answer = ask_wiki_question(repo_name, question)
            print(f"Got answer in {time.monotonic() - asked_at:.0f}s ({len(answer)} chars)")

            answer_file = save_answer(answer)
            if answer_file:
                found_count += 1
                print(f"Possible vulnerability, saved to {answer_file}")
            else:
                print("No vulnerability reported")

            save_to_validated(audit_file.name, extract_search_url(answer), answer_file)
            processed_files.add(audit_file.name)
            processed_count += 1

        except Exception as e:
            failed_count += 1
            print(f"Error processing {audit_file.name}: {e}")

        time.sleep(DELAY_BETWEEN_QUESTIONS)

    print("\n=== Summary ===")
    print(f"Total files: {total}")
    print(f"Processed: {processed_count}")
    print(f"Vulnerabilities saved: {found_count}")
    print(f"Failed: {failed_count}")
    print(f"Skipped: {skipped_count}")
    print(f"Elapsed: {(time.monotonic() - start) / 60:.1f} min")


if __name__ == "__main__":
    main()
