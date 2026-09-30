# [C] Bootimus 0.1.70 Broken Access Control via JWTMiddleware Authorization Bypass

## Summary
Severity: Critical
Advisory: CVE-2026-56115
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-23
Source: https://osv.dev/vulnerability/CVE-2026-56115
Type: osv

## Details
Bootimus through 0.1.70 contains a broken access control vulnerability that allows authenticated low-privileged users to perform administrative actions by exploiting missing role enforcement in the JWTMiddleware function in internal/auth/auth.go, which validates JWT tokens and account status but fails to inspect the is_admin flag. Attackers can send requests to any endpoint under the /api/users path to create new administrator accounts or reset administrator passwords, thereby gaining full control of the server and the ability to modify boot menus and installation scripts served to PXE clients.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56115.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-56115
- https://www.vulncheck.com/advisories/bootimus-broken-access-control-via-jwtmiddleware-authorization-bypass
- https://github.com/garybowers/bootimus
- https://github.com/garybowers/bootimus/issues/84
