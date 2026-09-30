# [H] Outline: OAuth Scope Validation Logic Error Allows Privilege Escalation to Wildcard API Access

## Summary
Severity: High
Advisory: CVE-2026-43886
Aliases: GHSA-7732-6qrg-wjf4
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:H/A:N)
Published: 2026-05-11
Source: https://osv.dev/vulnerability/CVE-2026-43886
Type: osv

## Details
Outline is a service that allows for collaborative documentation. From 0.84.0 to 1.6.1, a logic error in OAuthInterface.validateScope() uses Array.some() to validate requested OAuth scopes, causing the function to accept the entire scope array if any single scope is valid. An attacker can smuggle the wildcard * scope by requesting scope=read *, escalating a read-only OAuth token to full unrestricted API access including write, delete, and admin operations. This vulnerability is fixed in 1.7.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43886.json
- https://github.com/outline/outline/security/advisories/GHSA-7732-6qrg-wjf4
- https://nvd.nist.gov/vuln/detail/CVE-2026-43886
