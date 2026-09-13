# [M] RuoYi vulnerable to Denial of Service by attackers with admin privileges

## Summary
Severity: Medium
Advisory: GHSA-qq5h-rjj9-q9qg
CVE: CVE-2024-57439
CWE: CWE-281
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-01-29
Source: https://github.com/advisories/GHSA-qq5h-rjj9-q9qg
Type: github-advisory

## Affected
- Maven: `com.ruoyi:ruoyi` — affected >=0

## Details
An issue in the reset password interface of ruoyi v4.8.0 allows attackers with Admin privileges to cause a Denial of Service (DoS) by duplicating the login name of the account.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-57439
- https://gitee.com/y_project/RuoYi
- https://github.com/peccc/restful_vul/blob/main/ruoyi_dos/ruoyi_dos.md
- https://github.com/yangzongzhuan/RuoYi
- https://ruoyi.vip
