# [M] Apache HTTP Server: mod_authn_socache crash

## Summary
Severity: Medium
Advisory: BIT-apache-2026-33007
Aliases: CVE-2026-33007
Ecosystem: Bitnami
Published: 2026-05-05
Source: https://osv.dev/vulnerability/BIT-apache-2026-33007
Type: osv

## Affected
- Bitnami: `apache` — affected >=2.4.0 <2.4.67

## Details
A NULL pointer dereference in the mod_authn_socache in Apache HTTP Server 2.4.66 and earlier allows an unauthenticated remote user to crash a child process in a caching forward proxy configuration.

Users are recommended to upgrade to version 2.4.67, which fixes this issue.

## References
- http://www.openwall.com/lists/oss-security/2026/05/04/22
- https://httpd.apache.org/security/vulnerabilities_24.html
- https://nvd.nist.gov/vuln/detail/CVE-2026-33007
