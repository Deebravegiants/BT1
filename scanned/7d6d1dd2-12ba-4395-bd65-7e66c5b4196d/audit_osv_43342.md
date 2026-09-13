# [H] Semaphore UI: CSRF vulnerability on password change endpoint - No CSRF token or password confirmation

## Summary
Severity: High
Advisory: CVE-2026-73292
Aliases: GHSA-8cj9-r88m-8945, GO-2026-6370
CVSS: 8.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:L)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-73292
Type: osv

## Details
Semaphore UI is a web interface for managing DevOps tools. Prior to 2.18.21, the /api/users/{id}/password endpoint accepts a cross-site request using the authenticated user's semaphore session cookie without CSRF protection or current-password confirmation, allowing an unauthenticated attacker to change an administrator's or another user's password after user interaction. This issue is fixed in version 2.18.21.

## References
- https://github.com/semaphoreui/semaphore/releases/tag/v2.18.21
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73292.json
- https://github.com/semaphoreui/semaphore/security/advisories/GHSA-8cj9-r88m-8945
- https://nvd.nist.gov/vuln/detail/CVE-2026-73292
- https://github.com/semaphoreui/semaphore/commit/2d6e2e3eb10e8bf688e2ab59609b909a012fad4c
- https://github.com/semaphoreui/semaphore/commit/c59c3dc9035badcbf0609c7d35679c06e590a956
