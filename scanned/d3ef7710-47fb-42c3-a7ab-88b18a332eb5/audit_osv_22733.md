# [H] CVE-2022-37205

## Summary
Severity: High
Advisory: CVE-2022-37205
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-09-20
Source: https://osv.dev/vulnerability/CVE-2022-37205
Type: osv

## Details
JFinal CMS 5.1.0 is affected by: SQL Injection. These interfaces do not use the same component, nor do they have filters, but each uses its own SQL concatenation method, resulting in SQL injection.

## References
- https://github.com/AgainstTheLight/CVE-2022-37205/blob/main/README.md
- https://github.com/AgainstTheLight/someEXP_of_jfinal_cms/blob/main/jfinal_cms/sql8.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/37xxx/CVE-2022-37205.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-37205
