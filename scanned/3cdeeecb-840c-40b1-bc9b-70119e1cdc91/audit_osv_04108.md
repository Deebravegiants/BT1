# [H] Apache HTTP Server: HTTP/2 DoS by Memory Increase

## Summary
Severity: High
Advisory: BIT-apache-2025-53020
Aliases: CVE-2025-53020
Ecosystem: Bitnami
Published: 2025-07-16
Source: https://osv.dev/vulnerability/BIT-apache-2025-53020
Type: osv

## Affected
- Bitnami: `apache` — affected >=2.4.17 <2.4.64

## Details
Late Release of Memory after Effective Lifetime vulnerability in Apache HTTP Server.

This issue affects Apache HTTP Server: from 2.4.17 up to 2.4.63.

Users are recommended to upgrade to version 2.4.64, which fixes the issue.

## References
- https://httpd.apache.org/security/vulnerabilities_24.html
- https://nvd.nist.gov/vuln/detail/CVE-2025-53020
- http://www.openwall.com/lists/oss-security/2025/07/10/10
- https://lists.debian.org/debian-lts-announce/2025/08/msg00009.html
