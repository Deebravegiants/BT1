# [M] Apache HTTP Server: escalation of privilege through expressions in .htaccess in multiple modules

## Summary
Severity: Medium
Advisory: BIT-apache-2026-44119
Aliases: CVE-2026-44119
Ecosystem: Bitnami
Published: 2026-06-10
Source: https://osv.dev/vulnerability/BIT-apache-2026-44119
Type: osv

## Affected
- Bitnami: `apache` — affected >=2.4.0 <2.4.68

## Details
Improper Privilege Management vulnerability in Apache HTTP Server 2.4.67 and earlier allows local .htaccess authors to read files with the privileges of the httpd user.

This issue affects Apache HTTP Server: from through 2.4.67.

Users are recommended to upgrade to version 2.4.68, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/06/08/11
- https://httpd.apache.org/security/vulnerabilities_24.html
- https://nvd.nist.gov/vuln/detail/CVE-2026-44119
