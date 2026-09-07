# [M] Cross-site Scripting in github.com/greenpau/caddy-security

## Summary
Severity: Medium
Advisory: GHSA-ff72-ff42-c3gw
CVE: CVE-2024-21496
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-02-17
Source: https://github.com/advisories/GHSA-ff72-ff42-c3gw
Type: github-advisory

## Affected
- Go: `github.com/greenpau/caddy-security` — affected >=0

## Details
All versions of the package github.com/greenpau/caddy-security are vulnerable to Cross-site Scripting (XSS) via the Referer header, due to improper input sanitization. Although the Referer header is sanitized by escaping some characters that can allow XSS (e.g., [&], [<], [>], ["], [']), it does not account for the attack based on the JavaScript URL scheme (e.g., javascript:alert(document.domain)// payload). Exploiting this vulnerability may not be trivial, but it could lead to the execution of malicious scripts in the context of the target user’s browser, compromising user sessions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-21496
- https://github.com/greenpau/caddy-security/issues/267
- https://blog.trailofbits.com/2023/09/18/security-flaws-in-an-sso-plugin-for-caddy
- https://security.snyk.io/vuln/SNYK-GOLANG-GITHUBCOMGREENPAUCADDYSECURITY-6249860
- github.com/greenpau/caddy-security
