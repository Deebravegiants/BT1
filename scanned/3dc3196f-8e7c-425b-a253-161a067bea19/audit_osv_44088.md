# [M] CVE-2026-79483

## Summary
Severity: Medium
Advisory: CVE-2026-79483
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-08-31
Source: https://osv.dev/vulnerability/CVE-2026-79483
Type: osv

## Details
FastGPT Community Edition 4.10.0 through 4.14.0 are vulnerable to a NoSQL injection in the POST /api/core/chat/getHistories endpoint. An unauthenticated attacker can inject malicious NoSQL operators via crafted JSON payloads to bypass authorization checks, resulting in unauthorized access to chat history titles of all users across the platform.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/79xxx/CVE-2026-79483.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-79483
- https://github.com/ExploreIO/CVE-2026-79483-FastGPT-NoSQL-Injection
- https://github.com/labring/FastGPT
