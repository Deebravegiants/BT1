# [M] Apache HTTP Server: OOB Read in `merge_response_headers` can cause crash

## Summary
Severity: Medium
Advisory: BIT-apache-2026-43951
Aliases: CVE-2026-43951
Ecosystem: Bitnami
Published: 2026-06-10
Source: https://osv.dev/vulnerability/BIT-apache-2026-43951
Type: osv

## Affected
- Bitnami: `apache` — affected >=2.4.0 <2.4.68

## Details
Out-of-bounds Read vulnerability in Apache HTTP Server with mod_headers and mod_mime and multiple response languages.

This issue affects Apache HTTP Server: from 2.4.0 through 2.4.67.

## References
- http://www.openwall.com/lists/oss-security/2026/06/08/10
- https://httpd.apache.org/security/vulnerabilities_24.html
- https://nvd.nist.gov/vuln/detail/CVE-2026-43951
