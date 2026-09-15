# [C] Apache HTTP Server: mod_dav_fs protected directory access

## Summary
Severity: Critical
Advisory: BIT-apache-2026-42535
Aliases: CVE-2026-42535
Ecosystem: Bitnami
Published: 2026-06-10
Source: https://osv.dev/vulnerability/BIT-apache-2026-42535
Type: osv

## Affected
- Bitnami: `apache` — affected >=0 <2.4.68

## Details
A path handling issue in mod_dav_fs in Apache 2.4.67 and earlier allows a WebDAV content author to directly manipulate trusted DAV property databases, potentially causing child process crashes.

Users are recommended to upgrade to version 2.4.68, which fixes this issue.

## References
- http://www.openwall.com/lists/oss-security/2026/06/08/8
- https://httpd.apache.org/security/vulnerabilities_24.html
- https://nvd.nist.gov/vuln/detail/CVE-2026-42535
