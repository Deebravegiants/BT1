# [M] Improper Neutralization of HTTP Headers in github.com/greenpau/caddy-security

## Summary
Severity: Medium
Advisory: GHSA-r969-783f-6jqr
CVE: CVE-2024-21499
CWE: CWE-644
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-02-17
Source: https://github.com/advisories/GHSA-r969-783f-6jqr
Type: github-advisory

## Affected
- Go: `github.com/greenpau/caddy-security` — affected >=0

## Details
All versions of the package github.com/greenpau/caddy-security are vulnerable to HTTP Header Injection via the X-Forwarded-Proto header due to redirecting to the injected protocol.Exploiting this vulnerability could lead to bypass of security mechanisms or confusion in handling TLS.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-21499
- https://github.com/greenpau/caddy-security/issues/270
- https://blog.trailofbits.com/2023/09/18/security-flaws-in-an-sso-plugin-for-caddy
- https://security.snyk.io/vuln/SNYK-GOLANG-GITHUBCOMGREENPAUCADDYSECURITY-6249863
- github.com/greenpau/caddy-security
