# [H] Swing Music Swing Music - Missing Authentication

## Summary
Severity: High
Advisory: CVE-2026-72605
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-72605
Type: osv

## Details
A missing authentication vulnerability in Swing Music 3.0.0 allows unauthenticated remote attackers to create arbitrary user accounts via the POST /auth/profile/create endpoint. The endpoint is allowlisted from JWT verification, permitting unauthenticated account creation. An attacker can register an account and use it to access protected functionality on the server.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72605.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72605
- https://github.com/swingmx/swingmusic
