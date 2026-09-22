# [M] Grav < 1.0.0-rc.16 Authentication Bypass via token URL Parameter

## Summary
Severity: Medium
Advisory: CVE-2026-62386
Aliases: CVE-2026-63408, GHSA-4hpj-wmpw-ghwq
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-17
Source: https://osv.dev/vulnerability/CVE-2026-62386
Type: osv

## Details
The Grav API plugin (getgrav/grav-plugin-api) before 1.0.0-rc.16 accepts JWT access tokens through the ?token= URL query parameter on every API route (JwtAuthenticator::extractBearerToken fallback). Because tokens are embedded in URLs, they are logged verbatim in web server access logs, leaked via the Referer header, stored in browser history, and captured by upstream proxy and CDN logs, exposing valid admin access tokens. A leaked token grants unauthorized API access, including reading configuration and user data, creating admin accounts, modifying system settings, and deleting pages.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62386.json
- https://github.com/getgrav/grav/security/advisories/GHSA-4hpj-wmpw-ghwq
- https://nvd.nist.gov/vuln/detail/CVE-2026-62386
- https://www.vulncheck.com/advisories/grav-rc-16-authentication-bypass-via-token-url-parameter
- https://github.com/getgrav/grav
