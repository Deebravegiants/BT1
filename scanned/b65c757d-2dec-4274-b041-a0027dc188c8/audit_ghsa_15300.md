# [H] Owncast Cross-Site Request Forgery vulnerability

## Summary
Severity: High
Advisory: GHSA-v99w-r56h-g23v
CVE: CVE-2024-29026
CWE: CWE-352
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2024-08-05
Source: https://github.com/advisories/GHSA-v99w-r56h-g23v
Type: github-advisory

## Affected
- Go: `github.com/owncast/owncast` — affected >=0 <0.1.3

## Details
Owncast is an open source, self-hosted, decentralized, single user live video streaming and chat server. In versions 0.1.2 and prior, a lenient CORS policy allows attackers to make a cross origin request, reading privileged information. This can be used to leak the admin password. Commit 9215d9ba0f29d62201d3feea9e77dcd274581624 fixes this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-29026
- https://github.com/owncast/owncast/commit/9215d9ba0f29d62201d3feea9e77dcd274581624
- https://github.com/owncast/owncast
- https://github.com/owncast/owncast/blob/v0.1.2/router/middleware/auth.go#L32
- https://securitylab.github.com/advisories/GHSL-2023-261_Owncast
