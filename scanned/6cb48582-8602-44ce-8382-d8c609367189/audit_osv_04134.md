# [C] Apache HTTP Server: Heap Underflow in `ap_regname` via Signed Char Overflow

## Summary
Severity: Critical
Advisory: BIT-apache-2026-44631
Aliases: CVE-2026-44631
Ecosystem: Bitnami
Published: 2026-06-10
Source: https://osv.dev/vulnerability/BIT-apache-2026-44631
Type: osv

## Affected
- Bitnami: `apache` — affected >=2.4.0 <2.4.68

## Details
Buffer Underwrite vulnerability in Apache HTTP Server on crafted regular expressions in the configuration.

This issue affects Apache HTTP Server: from 2.4.0 through 2.4.67.

Users are recommended to upgrade to version 2.4.68, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/06/08/14
- https://httpd.apache.org/security/vulnerabilities_24.html
- https://nvd.nist.gov/vuln/detail/CVE-2026-44631
