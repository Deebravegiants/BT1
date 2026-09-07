# [M] rm: 'rm -rf ./' (and ./// variants) silently deletes current directory contents, bypassing dot protection

## Summary
Severity: Medium
Advisory: GHSA-89p7-7cq3-hhr2
CVE: CVE-2026-35363
CWE: CWE-22, CWE-693
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2026-07-06
Source: https://github.com/advisories/GHSA-89p7-7cq3-hhr2
Type: github-advisory

## Affected
- crates.io: `uu_rm` — affected >=0 <0.6.0

## Details
`rm -rf .` is correctly refused, but `clean_trailing_slashes` normalizes `.///` to `./` while `path_is_current_or_parent_directory` only matches `.`/`..` (and `/.`/`/..`), not `./` or `../`. So `rm -rf ./` recursively deletes the directory's contents and then prints a misleading `cannot remove './': Invalid input`.

**Impact:** all files/subdirectories in the current directory are silently deleted; the misleading error makes users miss the recovery window. Recommendation: handle trailing-slash variants in `path_is_current_or_parent_directory`.

**Remediation:** Acknowledged by Canonical; fixed in commit d0e5af23.

---
_Reported by Zellic in the *uutils coreutils Program Security Assessment* (prepared for Canonical, Jan 20 2026), audited commit `3a07ffc5a9bd4c283e75afa548ba1f1957bad242`. Finding 3.60. Credit: Zellic._

_Upstream tracking issue: https://github.com/uutils/coreutils/issues/9749 · CVE-2026-35363_

## References
- https://github.com/uutils/coreutils/security/advisories/GHSA-89p7-7cq3-hhr2
- https://nvd.nist.gov/vuln/detail/CVE-2026-35363
- https://github.com/uutils/coreutils/issues/9749
- https://github.com/uutils/coreutils
