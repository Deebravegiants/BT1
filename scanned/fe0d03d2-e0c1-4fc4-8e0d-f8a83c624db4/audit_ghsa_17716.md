# [M] RuoYi has insecure permissions

## Summary
Severity: Medium
Advisory: GHSA-h5jh-rp76-q242
CVE: CVE-2024-57438
CWE: CWE-276, CWE-863
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-01-29
Source: https://github.com/advisories/GHSA-h5jh-rp76-q242
Type: github-advisory

## Affected
- Maven: `com.ruoyi:ruoyi` — affected >=0

## Details
Insecure permissions in RuoYi v4.8.0 allows authenticated attackers to escalate privileges by assigning themselves higher level roles.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-57438
- https://gitee.com/y_project/RuoYi
- https://github.com/peccc/restful_vul/blob/main/ruoyi_insecure_role_assignments/ruoyi_insecure_role_assignments.md
- https://github.com/yangzongzhuan/RuoYi
- https://ruoyi.vip
