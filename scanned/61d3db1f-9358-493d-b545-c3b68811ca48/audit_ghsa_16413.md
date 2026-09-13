# [M] Authentication Bypass by Spoofing in github.com/greenpau/caddy-security

## Summary
Severity: Medium
Advisory: GHSA-vj36-3ccr-6563
CVE: CVE-2024-21494
CWE: CWE-290, CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-02-17
Source: https://github.com/advisories/GHSA-vj36-3ccr-6563
Type: github-advisory

## Affected
- Go: `github.com/greenpau/caddy-security` — affected >=0

## Details
All versions of the package github.com/greenpau/caddy-security are vulnerable to Authentication Bypass by Spoofing via the X-Forwarded-For header due to improper input sanitization. An attacker can spoof an IP address used in the user identity module (/whoami API endpoint). This could lead to unauthorized access if the system trusts this spoofed IP address.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-21494
- https://github.com/greenpau/caddy-security/issues/266
- https://blog.trailofbits.com/2023/09/18/security-flaws-in-an-sso-plugin-for-caddy
- https://security.snyk.io/vuln/SNYK-GOLANG-GITHUBCOMGREENPAUCADDYSECURITY-6249859
- github.com/greenpau/caddy-security
