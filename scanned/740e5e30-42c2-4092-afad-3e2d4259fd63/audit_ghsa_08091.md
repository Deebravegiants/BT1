# [M] Sync-in Server has a stored cross-site scripting (XSS) vulnerability

## Summary
Severity: Medium
Advisory: GHSA-9jmq-xgjm-p8c2
CVE: CVE-2025-67438
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-02-20
Source: https://github.com/advisories/GHSA-9jmq-xgjm-p8c2
Type: github-advisory

## Affected
- npm: `@sync-in/server` — affected >=0 <1.9.3

## Details
A Stored Cross-Site Scripting (XSS) vulnerability in Sync-in Server before 1.9.3 allows an authenticated attacker to execute arbitrary JavaScript in a victim's browser. By uploading a crafted SVG file containing a malicious payload, an attacker can access and exfiltrate sensitive information, including the user's session cookies.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-67438
- https://github.com/Sync-in/server/commit/a6276d067725637310e4e83a3eee337aae81f439
- https://gist.github.com/x0root/86db30af91bb0e1707eb7e57a049b6ad
- https://github.com/Sync-in/server
- https://github.com/Sync-in/server/releases/tag/v1.9.3
