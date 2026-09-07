# [M] Open Redirect in OAuth2 Proxy

## Summary
Severity: Medium
Advisory: GHSA-5m6c-jp6f-2vcv
CVE: CVE-2020-4037
CWE: CWE-601
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2021-12-20
Source: https://github.com/advisories/GHSA-5m6c-jp6f-2vcv
Type: github-advisory

## Affected
- Go: `github.com/oauth2-proxy/oauth2-proxy` — affected >=5.1.1 <6.0.0

## Details
### Impact
As users can provide a redirect address for the proxy to send the authenticated user to at the end of the authentication flow. This is expected to be the original URL that the user was trying to access.
This redirect URL is checked within the proxy and validated before redirecting the user to prevent malicious actors providing redirects to potentially harmful sites.

## References
- https://github.com/oauth2-proxy/oauth2-proxy/security/advisories/GHSA-5m6c-jp6f-2vcv
- https://nvd.nist.gov/vuln/detail/CVE-2020-4037
- https://github.com/oauth2-proxy/oauth2-proxy/commit/ee5662e0f5001d76ec76562bb605abbd07c266a2
- https://github.com/oauth2-proxy/oauth2-proxy/releases/tag/v6.0.0
