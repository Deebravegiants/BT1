# [M] id: groups= computed from real GID instead of effective GID

## Summary
Severity: Medium
Advisory: GHSA-47c7-qrm7-mqw7
CVE: CVE-2026-35370
CWE: CWE-273, CWE-863
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-07-06
Source: https://github.com/advisories/GHSA-47c7-qrm7-mqw7
Type: github-advisory

## Affected
- crates.io: `uu_id` — affected >=0 <0.6.0

## Details
The id utility in uutils coreutils miscalculates the groups= section of its output. The implementation uses a user's real GID instead of their effective GID to compute the group list, leading to potentially divergent output compared to GNU coreutils. Because many scripts and automated processes rely on the output of id to make security-critical access-control or permission decisions, this discrepancy can lead to unauthorized access or security misconfigurations.

---
_Zellic finding 3.72. Reported in the Zellic *uutils coreutils Program Security Assessment* (for Canonical, Jan 2026), audited commit `3a07ffc5a9bd4c283e75afa548ba1f1957bad242`._

## References
- https://github.com/uutils/coreutils/security/advisories/GHSA-47c7-qrm7-mqw7
- https://nvd.nist.gov/vuln/detail/CVE-2026-35370
- https://github.com/uutils/coreutils/issues/10006
- https://github.com/uutils/coreutils
