# [M] mv: symlinks expanded during cross-device move (resource exhaustion / data duplication)

## Summary
Severity: Medium
Advisory: GHSA-h444-6j9x-p8vh
CVE: CVE-2026-35365
CWE: CWE-400, CWE-59
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:L (CVSS_V3)
Published: 2026-07-06
Source: https://github.com/advisories/GHSA-h444-6j9x-p8vh
Type: github-advisory

## Affected
- crates.io: `uu_mv` — affected >=0 <0.7.0

## Details
When moving directories across filesystems, uutils `mv` dereferences symlinks inside the tree, copying their targets as real files/dirs instead of preserving the symlinks. GNU preserves symlinks by default. E.g. a `etc_link -> /etc` inside the source becomes a full copy of `/etc` at the destination.

**Impact:** (1) resource exhaustion — a small tree can expand into a huge copy (time/disk DoS); (2) unintended duplication of sensitive paths referenced by symlink; (3) symlink-loop amplification causing deep recursion. Recommendation: in cross-device fallback, detect symlinks via `symlink_metadata()` and recreate with `read_link()`/`symlink()`; add loop detection.

**Remediation:** Acknowledged by Canonical; fixed in commit 9654e4ab.

---
_Reported by Zellic in the *uutils coreutils Program Security Assessment* (prepared for Canonical, Jan 20 2026), audited commit `3a07ffc5a9bd4c283e75afa548ba1f1957bad242`. Finding 3.63. Credit: Zellic._

## References
- https://github.com/uutils/coreutils/security/advisories/GHSA-h444-6j9x-p8vh
- https://nvd.nist.gov/vuln/detail/CVE-2026-35365
- https://github.com/uutils/coreutils/pull/10546
- https://github.com/uutils/coreutils/commit/9654e4abaf24449ef2279e9a16963edb5c8b8fef
- https://github.com/uutils/coreutils
- https://github.com/uutils/coreutils/releases/tag/0.7.0
