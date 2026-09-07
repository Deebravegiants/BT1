# [M] MantisBT Vulnerable to Denial-of-Service (DoS) via Excessive Note Length

## Summary
Severity: Medium
Advisory: GHSA-r3jf-hm7q-qfw5
CVE: CVE-2025-46556
CWE: CWE-770
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-11-03
Source: https://github.com/advisories/GHSA-r3jf-hm7q-qfw5
Type: github-advisory

## Affected
- Packagist: `mantisbt/mantisbt` — affected >=0 <2.27.2

## Details
A lack of server-side validation for note length in MantisBT allows attackers to permanently corrupt issue activity logs by submitting extremely long notes (tested with 4,788,761 characters). Once such a note is added:

### Impact
- The entire activity stream becomes unviewable (UI fails to render).
- New notes cannot be displayed, effectively breaking all future collaboration on the issue.

### Patches
Fixed in 2.27.2.

### Workarounds
None

### Credits
Thanks to Mazen Mahmoud (@TheAmazeng) for reporting the vulnerability.

## References
- https://github.com/mantisbt/mantisbt/security/advisories/GHSA-r3jf-hm7q-qfw5
- https://nvd.nist.gov/vuln/detail/CVE-2025-46556
- https://github.com/mantisbt/mantisbt/commit/c99a41272532ba49b5c8dccb7797afead9864234
- https://github.com/mantisbt/mantisbt/commit/d5cec6bffb44d54bd412c186b9baa409b1aa4238
- https://github.com/mantisbt/mantisbt/commit/e9119c68b4a0eaa0bbde3deb121e81f5f7157361
- https://github.com/mantisbt/mantisbt
