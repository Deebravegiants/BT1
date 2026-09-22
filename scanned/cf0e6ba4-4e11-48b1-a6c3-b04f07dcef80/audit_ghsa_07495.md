# [M] printenv: environment variables with invalid UTF-8 are silently skipped (evades inspection)

## Summary
Severity: Medium
Advisory: GHSA-p7h3-7q52-72w8
CVE: CVE-2026-35366
CWE: CWE-116, CWE-754
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-07-06
Source: https://github.com/advisories/GHSA-p7h3-7q52-72w8
Type: github-advisory

## Affected
- crates.io: `uu_printenv` — affected >=0 <0.6.0

## Details
The printenv utility in uutils coreutils fails to display environment variables containing invalid UTF-8 byte sequences. While POSIX permits arbitrary bytes in environment strings, the uutils implementation silently skips these entries rather than printing the raw bytes. This vulnerability allows malicious environment variables (e.g., adversarial LD_PRELOAD values) to evade inspection by administrators or security auditing tools, potentially allowing library injection or other environment-based attacks to go undetected.

---
_Zellic finding 3.66. Reported in the Zellic *uutils coreutils Program Security Assessment* (for Canonical, Jan 2026), audited commit `3a07ffc5a9bd4c283e75afa548ba1f1957bad242`._

## References
- https://github.com/uutils/coreutils/security/advisories/GHSA-p7h3-7q52-72w8
- https://nvd.nist.gov/vuln/detail/CVE-2026-35366
- https://github.com/uutils/coreutils/issues/9701
- https://github.com/uutils/coreutils/pull/9728
- https://github.com/uutils/coreutils/commit/0bfbbc00c7895c0fb6ea94987b4aab99e3d7ee52
- https://github.com/uutils/coreutils
- https://github.com/uutils/coreutils/releases/tag/0.6.0
