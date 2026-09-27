# [C] Apache HTTP Server: mod_ldap per-dir use-after-free

## Summary
Severity: Critical
Advisory: BIT-apache-2026-29167
Aliases: CVE-2026-29167
Ecosystem: Bitnami
Published: 2026-06-10
Source: https://osv.dev/vulnerability/BIT-apache-2026-29167
Type: osv

## Affected
- Bitnami: `apache` — affected >=2.4.0 <2.4.68

## Details
Use After Free vulnerability in Apache HTTP Server with mod_ldap in per-directory configuration

This issue affects Apache HTTP Server: from 2.4.0 through 2.4.67.

Users are recommended to upgrade to version 2.4.68, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/06/08/4
- http://www.openwall.com/lists/oss-security/2026/06/09/1
- https://httpd.apache.org/security/vulnerabilities_24.html
- https://nvd.nist.gov/vuln/detail/CVE-2026-29167
