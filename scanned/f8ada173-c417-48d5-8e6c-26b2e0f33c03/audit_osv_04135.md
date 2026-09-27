# [H] Apache HTTP Server: mod_http2 memory corruption when file handles exhausted

## Summary
Severity: High
Advisory: BIT-apache-2026-48913
Aliases: CVE-2026-48913
Ecosystem: Bitnami
Published: 2026-06-10
Source: https://osv.dev/vulnerability/BIT-apache-2026-48913
Type: osv

## Affected
- Bitnami: `apache` — affected >=2.4.55 <2.4.68

## Details
Use After Free vulnerability in Apache HTTP Server module mod_http2 when file handles are already exhausted.

This issue affects Apache HTTP Server: from 2.4.55 through 2.4.67.

## References
- http://www.openwall.com/lists/oss-security/2026/06/08/15
- https://httpd.apache.org/security/vulnerabilities_24.html
- https://nvd.nist.gov/vuln/detail/CVE-2026-48913
