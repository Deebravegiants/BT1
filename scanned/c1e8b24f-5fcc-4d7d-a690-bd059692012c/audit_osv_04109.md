# [M] Apache HTTP Server: 'RewriteCond expr' always evaluates to true in 2.4.64

## Summary
Severity: Medium
Advisory: BIT-apache-2025-54090
Aliases: CVE-2025-54090
Ecosystem: Bitnami
Published: 2025-07-29
Source: https://osv.dev/vulnerability/BIT-apache-2025-54090
Type: osv

## Affected
- Bitnami: `apache` — affected >=2.4.64 <2.4.65

## Details
A bug in Apache HTTP Server 2.4.64 results in all "RewriteCond expr ..." tests evaluating as "true".



Users are recommended to upgrade to version 2.4.65, which fixes the issue.

## References
- https://httpd.apache.org/security/vulnerabilities_24.html
- https://news.ycombinator.com/item?id=44666896
- https://nvd.nist.gov/vuln/detail/CVE-2025-54090
- http://www.openwall.com/lists/oss-security/2025/07/24/2
- https://lists.debian.org/debian-lts-announce/2025/08/msg00009.html
