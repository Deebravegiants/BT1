# [M] Open Redirect in github.com/greenpau/caddy-security

## Summary
Severity: Medium
Advisory: GHSA-8hp3-rmr7-xh88
CVE: CVE-2024-21497
CWE: CWE-601
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-02-17
Source: https://github.com/advisories/GHSA-8hp3-rmr7-xh88
Type: github-advisory

## Affected
- Go: `github.com/greenpau/caddy-security` — affected >=0

## Details
All versions of the package github.com/greenpau/caddy-security are vulnerable to Open Redirect via the redirect_url parameter. An attacker could perform a phishing attack and trick users into visiting a malicious website by crafting a convincing URL with this parameter. To exploit this vulnerability, the user must take an action, such as clicking on a portal button or using the browser’s back button, to trigger the redirection.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-21497
- https://github.com/greenpau/caddy-security/issues/268
- https://blog.trailofbits.com/2023/09/18/security-flaws-in-an-sso-plugin-for-caddy
- https://security.snyk.io/vuln/SNYK-GOLANG-GITHUBCOMGREENPAUCADDYSECURITY-6249861
- github.com/greenpau/caddy-security
