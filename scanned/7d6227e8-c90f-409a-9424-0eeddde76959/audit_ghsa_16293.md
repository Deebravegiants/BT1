# [M] Server-Side Request Forgery in github.com/greenpau/caddy-security

## Summary
Severity: Medium
Advisory: GHSA-93x8-66j2-wwr5
CVE: CVE-2024-21498
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-02-17
Source: https://github.com/advisories/GHSA-93x8-66j2-wwr5
Type: github-advisory

## Affected
- Go: `github.com/greenpau/caddy-security` — affected >=0

## Details
All versions of the package github.com/greenpau/caddy-security are vulnerable to Server-side Request Forgery (SSRF) via X-Forwarded-Host header manipulation. An attacker can expose sensitive information, interact with internal services, or exploit other vulnerabilities within the network by exploiting this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-21498
- https://github.com/greenpau/caddy-security/issues/269
- https://blog.trailofbits.com/2023/09/18/security-flaws-in-an-sso-plugin-for-caddy
- https://security.snyk.io/vuln/SNYK-GOLANG-GITHUBCOMGREENPAUCADDYSECURITY-6249862
- github.com/greenpau/caddy-security
