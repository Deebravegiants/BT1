# [H] ApostropheCMS: 2nd-order prototype pollution via PATCH leading to single-request persistent DoS

## Summary
Severity: High
Advisory: GHSA-vmg4-6gfg-83qx
CVE: CVE-2026-71553
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-09-02
Source: https://github.com/advisories/GHSA-vmg4-6gfg-83qx
Type: github-advisory

## Affected
- npm: `apostrophe` — affected >=0

## Details
The vulnerability is a single-request persistent DoS by submitting e.g.
"PATCH /api/v1/article/<id>" with a valid editor session and body of
{"toString.call":"x"}, overwriting the global toString function with
value x.

Fabian

## References
- https://github.com/apostrophecms/apostrophe/security/advisories/GHSA-vmg4-6gfg-83qx
- https://nvd.nist.gov/vuln/detail/CVE-2026-71553
- https://github.com/apostrophecms/apostrophe/commit/5a3746aaed49761e171c2cbfe793267c959829fd
- https://github.com/apostrophecms/apostrophe
