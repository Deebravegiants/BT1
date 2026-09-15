# [H] Apache HTTP Server: mod_md unrestricted OCSP response

## Summary
Severity: High
Advisory: BIT-apache-2026-29168
Aliases: CVE-2026-29168
Ecosystem: Bitnami
Published: 2026-05-07
Source: https://osv.dev/vulnerability/BIT-apache-2026-29168
Type: osv

## Affected
- Bitnami: `apache` — affected >=2.4.30 <2.4.67

## Details
Allocation of Resources Without Limits or Throttling vulnerability in Apache HTTP Server's  mod_md via OCSP response data.

This issue affects Apache HTTP Server: from 2.4.30 through 2.4.66.

Users are recommended to upgrade to version 2.4.67, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/05/05/6
- https://httpd.apache.org/security/vulnerabilities_24.html
- https://nvd.nist.gov/vuln/detail/CVE-2026-29168
