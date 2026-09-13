# [M] CVE-2024-54762

## Summary
Severity: Medium
Advisory: CVE-2024-54762
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L)
Published: 2025-01-09
Source: https://osv.dev/vulnerability/CVE-2024-54762
Type: osv

## Details
Ruoyi v.4.7.9 and before contains an authenticated SQL injection vulnerability. This is because the filterKeyword method does not completely filter SQL injection keywords, resulting in the risk of SQL injection.

## References
- https://github.com/yangzongzhuan/RuoYi/
- https://locrian-lightning-dc7.notion.site/CVE-2024-54762-1748e5e2b1a280b4a549dcce2c4823e8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/54xxx/CVE-2024-54762.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-54762
