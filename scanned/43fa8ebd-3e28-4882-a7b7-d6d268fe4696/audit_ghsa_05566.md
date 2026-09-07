# [M] filelock Time-of-Check-Time-of-Use (TOCTOU) Symlink Vulnerability in SoftFileLock

## Summary
Severity: Medium
Advisory: GHSA-qmgc-5h2g-mvrw
CVE: CVE-2026-22701
CWE: CWE-362, CWE-367, CWE-59
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:L/A:H (CVSS_V3)
Published: 2026-01-13
Source: https://github.com/advisories/GHSA-qmgc-5h2g-mvrw
Type: github-advisory

## Affected
- PyPI: `filelock` — affected >=0 <3.20.3

## Details
## Vulnerability Summary

**Title:** Time-of-Check-Time-of-Use (TOCTOU) Symlink Vulnerability in SoftFileLock

**Affected Component:** `filelock` package - `SoftFileLock` class
**File:** `src/filelock/_soft.py` lines 17-27
**CWE:** CWE-362, CWE-367, CWE-59

---

## Description

A TOCTOU race condition vulnerability exists in the `SoftFileLock` implementation of the filelock package. An attacker with local filesystem access and permission to create symlinks can exploit a race condition between the permission validation and file creation to cause lock operations to fail or behave unexpectedly.

The vulnerability occurs in the `_acquire()` method between `raise_on_not_writable_file()` (permission check) and `os.open()` (file creation). During this race window, an attacker can create a symlink at the lock file path, potentially causing the lock to operate on an unintended target file or leading to denial of service.

### Attack Scenario

```
1. Lock attempts to acquire on /tmp/app.lock
2. Permission validation passes
3. [RACE WINDOW] - Attacker creates: ln -s /tmp/important.txt /tmp/app.lock
4. os.open() tries to create lock file
5. Lock operates on attacker-controlled target file or fails
```

---

## Impact

_What kind of vulnerability is it? Who is impacted?_

This is a **Time-of-Check-Time-of-Use (TOCTOU) race condition vulnerability** affecting any application using `SoftFileLock` for inter-process synchronization.

**Affected Users:**
- Applications using `filelock.SoftFileLock` directly
- Applications using the fallback `FileLock` on systems without `fcntl` support (e.g., GraalPy)

**Consequences:**
- **Silent lock acquisition failure** - applications may not detect that exclusive resource access is not guaranteed
- **Denial of Service** - attacker can prevent lock file creation by maintaining symlink
- **Resource serialization failures** - multiple processes may acquire "locks" simultaneously
- **Unintended file operations** - lock could operate on attacker-controlled files

**CVSS v4.0 Score:** 5.6 (Medium)
**Vector:** CVSS:4.0/AV:L/AT:L/PR:L/UI:N/VC:N/VI:L/VA:H/SC:N/SI:N/SA:N

**Attack Requirements:**
- Local filesystem access to the directory containing lock files
- Permission to create symlinks (standard for regular unprivileged users on Unix/Linux)
- Ability to time the symlink creation during the narrow race window

---

## Patches

_Has the problem been patched? What versions should users upgrade to?_

Yes, the vulnerability has been patched by adding the `O_NOFOLLOW` flag to prevent symlink following during lock file creation.

**Patched Version:** Next release (commit: 255ed068bc85d1ef406e50a135e1459170dd1bf0)

**Mitigation Details:**
- The `O_NOFOLLOW` flag is added conditionally and gracefully degrades on platforms without support
- On platforms with `O_NOFOLLOW` support (most modern systems): symlink attacks are completely prevented
- On platforms without `O_NOFOLLOW` (e.g., GraalPy): TOCTOU window remains but is documented

**Users should:**
- Upgrade to the patched version when available
- For critical deployments, consider using `UnixFileLock` or `WindowsFileLock` instead of the fallback `SoftFileLock`

---

## Workarounds

_Is there a way for users to fix or remediate the vulnerability without upgrading?_

For users unable to update immediately:

1. **Avoid `SoftFileLock` in security-sensitive contexts** - use `UnixFileLock` or `WindowsFileLock` when available (these were already patched for CVE-2025-68146)

2. **Restrict filesystem permissions** - prevent untrusted users from creating symlinks in lock file directories:
   ```bash
   chmod 700 /path/to/lock/directory
   ```

3. **Use process isolation** - isolate untrusted code from lock file paths to prevent symlink creation

4. **Monitor lock operations** - implement application-level checks to verify lock acquisitions are successful before proceeding with critical operations

---

## References

_Are there any links users can visit to find out more?_

- **Similar Vulnerability:** CVE-2025-68146 (TOCTOU vulnerability in UnixFileLock/WindowsFileLock)
- **CWE-362 (Concurrent Execution using Shared Resource):** https://cwe.mitre.org/data/definitions/362.html
- **CWE-367 (Time-of-check Time-of-use Race Condition):** https://cwe.mitre.org/data/definitions/367.html
- **CWE-59 (Improper Link Resolution Before File Access):** https://cwe.mitre.org/data/definitions/59.html
- **O_NOFOLLOW documentation:** https://man7.org/linux/man-pages/man2/open.2.html
- **GitHub Repository:** https://github.com/tox-dev/filelock

---

**Reported by:** George Tsigourakos (@tsigouris007)

## References
- https://github.com/tox-dev/filelock/security/advisories/GHSA-qmgc-5h2g-mvrw
- https://nvd.nist.gov/vuln/detail/CVE-2026-22701
- https://github.com/tox-dev/filelock/commit/255ed068bc85d1ef406e50a135e1459170dd1bf0
- https://github.com/tox-dev/filelock/commit/41b42dd2c72aecf7da83dbda5903b8087dddc4d5
- https://github.com/tox-dev/filelock
