# [H] Apache HTTP Server: Server Side Includes adds query string to #exec cmd=...

## Summary
Severity: High
Advisory: BIT-apache-2025-58098
Aliases: CVE-2025-58098
Ecosystem: Bitnami
Published: 2025-12-09
Source: https://osv.dev/vulnerability/BIT-apache-2025-58098
Type: osv

## Affected
- Bitnami: `apache` — affected >=0 <2.4.66

## Details
Apache HTTP Server 2.4.65 and earlier with Server Side Includes (SSI) enabled and mod_cgid (but not mod_cgi) passes the shell-escaped query string to #exec cmd="..." directives.

This issue affects Apache HTTP Server before 2.4.66.

Users are recommended to upgrade to version 2.4.66, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2025/12/04/5
- https://httpd.apache.org/security/vulnerabilities_24.html
- https://nvd.nist.gov/vuln/detail/CVE-2025-58098
