# [H] Apache HTTP Server: mod_proxy_ajp: Heap Over-Read and memory disclosure in  ajp_parse_data()

## Summary
Severity: High
Advisory: BIT-apache-2026-34059
Aliases: CVE-2026-34059
Ecosystem: Bitnami
Published: 2026-05-05
Source: https://osv.dev/vulnerability/BIT-apache-2026-34059
Type: osv

## Affected
- Bitnami: `apache` — affected >=0 <2.4.67

## Details
Buffer Over-read vulnerability in Apache HTTP Server.

This issue affects Apache HTTP Server: through 2.4.66.

Users are recommended to upgrade to version 2.4.67, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/05/04/17
- https://httpd.apache.org/security/vulnerabilities_24.html
- https://nvd.nist.gov/vuln/detail/CVE-2026-34059
