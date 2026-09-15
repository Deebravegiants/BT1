# [H] Apache HTTP Server: mod_ssl error log variable escaping

## Summary
Severity: High
Advisory: BIT-apache-2024-47252
Aliases: CVE-2024-47252
Ecosystem: Bitnami
Published: 2025-07-16
Source: https://osv.dev/vulnerability/BIT-apache-2024-47252
Type: osv

## Affected
- Bitnami: `apache` — affected >=2.4.0 <2.4.64

## Details
Insufficient escaping of user-supplied data in mod_ssl in Apache HTTP Server 2.4.63 and earlier allows an untrusted SSL/TLS client to insert escape characters into log files in some configurations.

In a logging configuration where CustomLog is used with "%{varname}x" or "%{varname}c" to log variables provided by mod_ssl such as SSL_TLS_SNI, no escaping is performed by either mod_log_config or mod_ssl and unsanitized data provided by the client may appear in log files.

## References
- https://httpd.apache.org/security/vulnerabilities_24.html
- https://nvd.nist.gov/vuln/detail/CVE-2024-47252
- http://www.openwall.com/lists/oss-security/2025/07/10/2
- http://www.openwall.com/lists/oss-security/2025/07/10/6
- https://lists.debian.org/debian-lts-announce/2025/08/msg00009.html
