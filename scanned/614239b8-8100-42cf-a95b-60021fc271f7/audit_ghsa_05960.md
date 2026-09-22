# [M] CodeIgniter: Spoofable forwarded HTTPS headers in IncomingRequest::isSecure()

## Summary
Severity: Medium
Advisory: GHSA-7wmf-pw8j-mc78
CVE: CVE-2026-63220
CWE: CWE-348
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-08-07
Source: https://github.com/advisories/GHSA-7wmf-pw8j-mc78
Type: github-advisory

## Affected
- Packagist: `codeigniter4/framework` — affected >=0 <4.7.4

## Details
### Impact
`IncomingRequest::isSecure()` trusted the `X-Forwarded-Proto` and `Front-End-Https` headers from any incoming request. In affected deployments, an attacker could spoof these headers and cause the application to incorrectly treat an HTTP request as secure.

This may impact applications that rely on `isSecure()`, `force_https()`, `forceGlobalSecureRequests`, or similar logic to enforce HTTPS-only access or make security-sensitive decisions.

Exploitability depends on deployment configuration. Applications are most exposed if the backend is reachable directly over HTTP, or if a reverse proxy/load balancer forwards client-supplied forwarding headers without stripping or overwriting them.

### Patches
Upgrade to v4.7.4 or later.

### Workarounds
Users who cannot upgrade immediately should enforce HTTP-to-HTTPS redirects outside CodeIgniter, for example with Apache `.htaccess`/virtual host rules, nginx server blocks, Caddy site config, or load balancer redirect rules.

Users should also ensure that reverse proxies strip or overwrite client-supplied `X-Forwarded-Proto` and `Front-End-Https` headers before forwarding requests to the application.

## References
- https://github.com/codeigniter4/CodeIgniter4/security/advisories/GHSA-7wmf-pw8j-mc78
- https://nvd.nist.gov/vuln/detail/CVE-2026-63220
- https://github.com/codeigniter4/CodeIgniter4/commit/ecbf044666bed41d23f07518096d9843fe6c08b0
- https://github.com/codeigniter4/CodeIgniter4
- https://github.com/codeigniter4/CodeIgniter4/releases/tag/v4.7.4
