# [H] File Browser 2.50.0 through 2.63.21 JWT Expiration Bypass

## Summary
Severity: High
Advisory: CVE-2026-73611
Aliases: GHSA-v3jv-rmh2-635j
CVSS: 7.5 (CVSS:4.0/AV:N/AC:H/AT:P/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-73611
Type: osv

## Details
File Browser versions from 2.50.0 through 2.63.21 fail to validate JWT expiration when proxy authentication is configured with a non-default logout page. Attackers with a previously valid token can access protected routes and administrative endpoints indefinitely, and exchange expired tokens for fresh ones via the renewal endpoint.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73611.json
- https://github.com/filebrowser/filebrowser/security/advisories/GHSA-v3jv-rmh2-635j
- https://nvd.nist.gov/vuln/detail/CVE-2026-73611
- https://www.vulncheck.com/advisories/file-browser-through-jwt-expiration-bypass
- https://github.com/filebrowser/filebrowser/commit/72faf6dd3c85628e332d3e567124b86708ce2695
