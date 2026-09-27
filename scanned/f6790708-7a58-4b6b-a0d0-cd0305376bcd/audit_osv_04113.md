# [M] Apache HTTP Server: mod_userdir+suexec bypass via AllowOverride FileInfo

## Summary
Severity: Medium
Advisory: BIT-apache-2025-66200
Aliases: CVE-2025-66200
Ecosystem: Bitnami
Published: 2025-12-09
Source: https://osv.dev/vulnerability/BIT-apache-2025-66200
Type: osv

## Affected
- Bitnami: `apache` — affected >=2.4.7 <2.4.66

## Details
mod_userdir+suexec bypass via AllowOverride FileInfo vulnerability in Apache HTTP Server. Users with access to use the RequestHeader directive in htaccess can cause some CGI scripts to run under an unexpected userid.

This issue affects Apache HTTP Server: from 2.4.7 through 2.4.65.

Users are recommended to upgrade to version 2.4.66, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2025/12/04/8
- https://httpd.apache.org/security/vulnerabilities_24.html
- https://nvd.nist.gov/vuln/detail/CVE-2025-66200
