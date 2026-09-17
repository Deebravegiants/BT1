# [M] OpenSIPS 3.1 <= 3.6.4 auth_jwt SQL Injection Enables JWT Authentication Bypass

## Summary
Severity: Medium
Advisory: CVE-2026-25554
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N)
Published: 2026-02-25
Source: https://osv.dev/vulnerability/CVE-2026-25554
Type: osv

## Details
OpenSIPS versions 3.1 before 3.6.4 containing the auth_jwt module (prior to commit 3822d33) contain a SQL injection vulnerability in the jwt_db_authorize() function in modules/auth_jwt/authorize.c when db_mode is enabled and a SQL database backend is used. The function extracts the tag claim from a JWT without prior signature verification and incorporates the unescaped value directly into a SQL query. An attacker can supply a crafted JWT with a malicious tag claim to manipulate the query result and bypass JWT authentication, allowing impersonation of arbitrary identities.

## References
- https://opensips.org/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25554.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-25554
- https://opensips.org/pub/opensips/3.6.4/ChangeLog
- https://www.vulncheck.com/advisories/opensips-auth-jwt-sql-injection-enables-jwt-authentication-bypass
- https://github.com/OpenSIPS/opensips/pull/3807
- https://github.com/OpenSIPS/opensips/commit/3822d33c1c6b25832fdd88da1d23eed74be55b05
- https://github.com/OpenSIPS/opensips
