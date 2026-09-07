# [H] RuoYi allowed unauthorized attackers to view the session ID of the admin in the system monitoring

## Summary
Severity: High
Advisory: GHSA-v664-qgx9-wf79
CVE: CVE-2024-57436
CWE: CWE-200, CWE-922
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-01-29
Source: https://github.com/advisories/GHSA-v664-qgx9-wf79
Type: github-advisory

## Affected
- Maven: `com.ruoyi:ruoyi` — affected >=0

## Details
RuoYi v4.8.0 was discovered to allow unauthorized attackers to view the session ID of the admin in the system monitoring. This issue can allow attackers to impersonate Admin users via using a crafted cookie.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-57436
- https://gitee.com/y_project/RuoYi
- https://github.com/peccc/restful_vul/blob/main/ruoyi_elevation_of_privileges/ruoyi_elevation_of_privileges.md
- https://github.com/yangzongzhuan/RuoYi
- https://ruoyi.vip
