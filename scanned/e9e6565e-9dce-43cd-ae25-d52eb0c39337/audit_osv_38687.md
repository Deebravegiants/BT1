# [H] AdGuard Home Authentication Bypass via Path Traversal in Admin-Token Cookie

## Summary
Severity: High
Advisory: CVE-2026-41448
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-06-08
Source: https://osv.dev/vulnerability/CVE-2026-41448
Type: osv

## Details
AdGuard Home, when started with the --glinet flag, contains an authentication bypass vulnerability that allows unauthenticated attackers to gain full admin access by supplying a path traversal sequence in the Admin-Token cookie, exploiting unsanitized string concatenation in the token file path construction within the authglinet middleware. Attackers can craft a request with a traversal payload in the Admin-Token header to redirect file reads to arbitrary paths.

## References
- https://github.com/AdguardTeam/AdGuardHome/releases/tag/v0.107.77
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41448.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-41448
- https://www.vulncheck.com/advisories/adguard-home-authentication-bypass-via-path-traversal-in-admin-token-cookie
- https://github.com/AdguardTeam/AdGuardHome
