# [M] changedetection.io - No Rate Limiting on /login Enables Unlimited Password Brute-Force

## Summary
Severity: Medium
Advisory: CVE-2026-71205
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-71205
Type: osv

## Details
changedetection.io's /login route checks the submitted password against a single PBKDF2-HMAC-SHA256 hash with no per-IP or per-session rate limiting, failed-attempt counter, or lockout (no rate-limiting library is present in requirements.txt).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71205.json
- https://github.com/dgtlmoon/changedetection.io
- https://nvd.nist.gov/vuln/detail/CVE-2026-71205
