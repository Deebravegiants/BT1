# [M] virtualenv Has TOCTOU Vulnerabilities in Directory Creation

## Summary
Severity: Medium
Advisory: GHSA-597g-3phw-6986
CVE: CVE-2026-22702
CWE: CWE-362, CWE-59
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-01-13
Source: https://github.com/advisories/GHSA-597g-3phw-6986
Type: github-advisory

## Affected
- PyPI: `virtualenv` — affected >=0 <20.36.1

## Details
## Impact

TOCTOU (Time-of-Check-Time-of-Use) vulnerabilities in `virtualenv` allow local attackers to perform symlink-based attacks on directory creation operations. An attacker with local access can exploit a race condition between directory existence checks and creation to redirect virtualenv's app_data and lock file operations to attacker-controlled locations.

**Affected versions:** All versions up to and including 20.36.1

**Affected users:** Any user running `virtualenv` on multi-user systems where untrusted local users have filesystem access to shared temporary directories or where `VIRTUALENV_OVERRIDE_APP_DATA` points to a user-writable location.

**Attack scenarios:**
- Cache poisoning: Attacker corrupts wheels or Python metadata in the cache
- Information disclosure: Attacker reads sensitive cached data or metadata
- Lock bypass: Attacker controls lock file semantics to cause concurrent access violations
- Denial of service: Lock starvation preventing virtualenv operations

## Patches

The vulnerability has been patched by replacing check-then-act patterns with atomic `os.makedirs(..., exist_ok=True)` operations.

**Fixed in:** PR #3013

**Versions with the fix:** 20.36.2 and later

Users should upgrade to version 20.36.2 or later.

## Workarounds

If you cannot upgrade immediately:

1. Ensure `VIRTUALENV_OVERRIDE_APP_DATA` points to a directory owned by the current user with restricted permissions (mode 0700)
2. Avoid running `virtualenv` in shared temporary directories where other users have write access
3. Use separate user accounts for different projects to isolate app_data directories

## References

- GitHub PR: https://github.com/pypa/virtualenv/pull/3013
- Vulnerability reported by: @tsigouris007
- CWE-362: Concurrent Execution using Shared Resource with Improper Synchronization (TOCTOU)
- CWE-59: Improper Link Resolution Before File Access

## References
- https://github.com/pypa/virtualenv/security/advisories/GHSA-597g-3phw-6986
- https://nvd.nist.gov/vuln/detail/CVE-2026-22702
- https://github.com/pypa/virtualenv/pull/3013
- https://github.com/pypa/virtualenv/commit/dec4cec5d16edaf83a00a658f32d1e032661cebc
- https://github.com/pypa/virtualenv
