# [M] MCPHub has an authentication bypass

## Summary
Severity: Medium
Advisory: GHSA-9vq7-9h42-j88h
CVE: CVE-2025-13822
CWE: CWE-639
Ecosystem: npm
CVSS: CVSS:4.0/AV:A/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-9vq7-9h42-j88h
Type: github-advisory

## Affected
- npm: `@samanhappy/mcphub` — affected >=0 <0.11.0

## Details
MCPHub in versions below 0.11.0 is vulnerable to authentication bypass. Some endpoints are not protected by authentication middleware, allowing an unauthenticated attacker to perform actions in the name of other users and using their privileges.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-13822
- https://cert.pl/en/posts/2026/04/CVE-2025-13822
- https://github.com/samanhappy/mcphub
