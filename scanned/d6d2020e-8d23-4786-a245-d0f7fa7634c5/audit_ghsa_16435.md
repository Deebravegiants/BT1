# [M] Improper Validation of Array Index in github.com/greenpau/caddy-security

## Summary
Severity: Medium
Advisory: GHSA-8h95-jcp5-pjpr
CVE: CVE-2024-21493
CWE: CWE-129
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2024-02-17
Source: https://github.com/advisories/GHSA-8h95-jcp5-pjpr
Type: github-advisory

## Affected
- Go: `github.com/greenpau/caddy-security` — affected >=0

## Details
All versions of the package github.com/greenpau/caddy-security are vulnerable to Improper Validation of Array Index when parsing a Caddyfile. Multiple parsing functions in the affected library do not validate whether their input values are nil before attempting to access elements, which can lead to a panic (index out of range). Panics during the parsing of a configuration file may introduce ambiguity and vulnerabilities, hindering the correct interpretation and configuration of the web server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-21493
- https://github.com/greenpau/caddy-security/issues/263
- https://blog.trailofbits.com/2023/09/18/security-flaws-in-an-sso-plugin-for-caddy
- https://security.snyk.io/vuln/SNYK-GOLANG-GITHUBCOMGREENPAUCADDYSECURITY-5961078
- github.com/greenpau/caddy-security
