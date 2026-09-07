# [M] caddy-security plugin for Caddy vulnerable to reflected Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-xwmv-cx7p-fqfc
CVE: CVE-2023-52430
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-02-13
Source: https://github.com/advisories/GHSA-xwmv-cx7p-fqfc
Type: github-advisory

## Affected
- Go: `github.com/greenpau/caddy-security` — affected >=0

## Details
The caddy-security plugin 1.1.20 for Caddy allows reflected XSS via a GET request to a URL that contains an XSS payload and begins with either a /admin or /settings/mfa/delete/ substring.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-52430
- https://github.com/greenpau/caddy-security/issues/264
- https://blog.trailofbits.com/2023/09/18/security-flaws-in-an-sso-plugin-for-caddy
- https://github.com/greenpau/caddy-security
