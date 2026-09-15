# [M] Apache HTTP Server: Off-by-one OOB reads in AJP getter functions

## Summary
Severity: Medium
Advisory: BIT-apache-2026-33857
Aliases: CVE-2026-33857
Ecosystem: Bitnami
Published: 2026-05-05
Source: https://osv.dev/vulnerability/BIT-apache-2026-33857
Type: osv

## Affected
- Bitnami: `apache` — affected >=0 <2.4.67

## Details
Out-of-bounds Read vulnerability in mod_proxy_ajp of 

Apache HTTP Server.

This issue affects Apache HTTP Server: through 2.4.66.

Users are recommended to upgrade to version 2.4.67, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/05/04/15
- https://httpd.apache.org/security/vulnerabilities_24.html
- https://nvd.nist.gov/vuln/detail/CVE-2026-33857
