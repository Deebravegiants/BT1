# [M] pyLoad Has Incomplete Fix for CVE-2026-33509 -storage_folder Bypass via Session Directory in pyLoad

## Summary
Severity: Medium
Advisory: GHSA-w727-595x-pc3r
CVE: CVE-2026-45306
CWE: CWE-706
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-w727-595x-pc3r
Type: github-advisory

## Affected
- PyPI: `pyload-ng` — affected >=0

## Details
## Summary
The fix for CVE-2026-33509 prevents setting `storage_folder` inside `PKGDIR` or `userdir`, but does NOT protect the Flask session directory (`/tmp/pyLoad/flask`). An authenticated attacker can set `storage_folder` to the session directory and download session files of other users via `/files/get/`, leading to account takeover.

## Details

The fix in `src/pyload/core/api/__init__.py`:

```python
directories = [PKGDIR, userdir]
if any(directories[0].startswith(d) for d in directories[1:]):
    return  # blocked
```

But the Flask session directory is:
```python
session_storage_path = os.path.join(api.get_cachedir(), "flask")
# = /tmp/pyLoad/flask  ← NOT blocked by fix
```

## Attack Chain

1. Attacker (admin) sets `storage_folder = /tmp/pyLoad/flask`
2. Fix does NOT block this — `/tmp/pyLoad/flask` not inside `PKGDIR` or `userdir`
3. Attacker requests `GET /files/get/<victim_session_filename>`
4. `send_from_directory('/tmp/pyLoad/flask', session_file)` serves victim's session
5. Attacker uses stolen session → **Account Takeover**

## PoC

<img width="592" height="408" alt="POC" src="https://github.com/user-attachments/assets/936b9f56-325b-437d-9edd-e0d5bb995187" />

```python
import os

PKGDIR = "/usr/lib/python3/dist-packages/pyload"
userdir = os.path.expanduser("~/.pyload")
session_dir = "/tmp/pyLoad/flask"

correct_case = lambda x: x
directories = [
    correct_case(os.path.join(os.path.realpath(d), ""))
    for d in [session_dir, PKGDIR, userdir]
]
blocked = any(directories[0].startswith(d) for d in directories[1:])

print(f"Fix blocks session_dir: {blocked}")
# Output: Fix blocks session_dir: False  ← BYPASS CONFIRMED
```

## Impact
Authenticated admin can steal sessions of other users → Account Takeover.

## Suggested Fix
```python
blocked_dirs = [PKGDIR, userdir, api.get_cachedir()]
directories = [
    os.path.join(os.path.realpath(d), "")
    for d in [value] + blocked_dirs
]
if any(directories[0].startswith(d) for d in directories[1:]):
    return
```

## References
- https://github.com/pyload/pyload/security/advisories/GHSA-w727-595x-pc3r
- https://nvd.nist.gov/vuln/detail/CVE-2026-45306
- https://github.com/advisories/GHSA-r7mc-x6x7-cqxx
- https://github.com/pyload/pyload
