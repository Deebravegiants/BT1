# [M] rm: --preserve-root bypassed via a symlink to / (string check instead of dev/inode)

## Summary
Severity: Medium
Advisory: GHSA-7cr3-h577-g38j
CVE: CVE-2026-35349
CWE: CWE-59, CWE-693
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-07-06
Source: https://github.com/advisories/GHSA-7cr3-h577-g38j
Type: github-advisory

## Affected
- crates.io: `uu_rm` — affected >=0 <0.7.0

## Details
The `--preserve-root` check uses a path-string test (`path.has_root() && path.parent().is_none()`) rather than comparing device/inode. A symlink to `/` (e.g. `/tmp/rootlink -> /`) has a parent component, so it passes the check. GNU caches `/`'s dev/inode at startup and compares every traversed directory against it.

**Impact:** `rm -rf --preserve-root` on a path that resolves through a symlink to `/` bypasses protection and can delete system directories. Recommendation: compare each entered directory's dev/inode against cached `/`.

**Remediation:** Acknowledged by Canonical; fixed in commit 5e5968cd.

---
_Reported by Zellic in the *uutils coreutils Program Security Assessment* (prepared for Canonical, Jan 20 2026), audited commit `3a07ffc5a9bd4c283e75afa548ba1f1957bad242`. Finding 3.44. Credit: Zellic._

## References
- https://github.com/uutils/coreutils/security/advisories/GHSA-7cr3-h577-g38j
- https://nvd.nist.gov/vuln/detail/CVE-2026-35349
- https://github.com/uutils/coreutils/pull/9706
- https://github.com/uutils/coreutils/commit/5e5968cdbc6618acd6c2402a8a98b503f278835e
- https://github.com/uutils/coreutils
- https://github.com/uutils/coreutils/releases/tag/0.7.0
