# [H] BIT-seopanel-2021-28419

## Summary
Severity: High
Advisory: BIT-seopanel-2021-28419
Aliases: CVE-2021-28419
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-seopanel-2021-28419
Type: osv

## Affected
- Bitnami: `seopanel` — affected >=4.8.0

## Details
The "order_col" parameter in archive.php of SEO Panel 4.8.0 is vulnerable to time-based blind SQL injection, which leads to the ability to retrieve all databases.

## References
- http://packetstormsecurity.com/files/162322/SEO-Panel-4.8.0-SQL-Injection.html
- https://github.com/seopanel/Seo-Panel/issues/209
