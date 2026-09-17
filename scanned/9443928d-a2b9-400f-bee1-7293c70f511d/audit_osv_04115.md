# [H] Apache HTTP Server: mod_rewrite elevation of privileges via ap_expr

## Summary
Severity: High
Advisory: BIT-apache-2026-24072
Aliases: CVE-2026-24072
Ecosystem: Bitnami
Published: 2026-05-05
Source: https://osv.dev/vulnerability/BIT-apache-2026-24072
Type: osv

## Affected
- Bitnami: `apache` — affected >=0 <2.4.67

## Details
An escalation of privilege bug in various modules in Apache HTTP 2.4.66 and earlier allows local .htaccess authors to read files with the privileges of the httpd user.

Users are recommended to upgrade to version 2.4.67, which fixes this issue.

## References
- http://www.openwall.com/lists/oss-security/2026/05/04/18
- https://httpd.apache.org/security/vulnerabilities_24.html
- https://nvd.nist.gov/vuln/detail/CVE-2026-24072
