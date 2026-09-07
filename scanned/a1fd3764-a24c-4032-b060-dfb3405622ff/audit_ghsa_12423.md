# [C] Jeecg Boot SQL Injection

## Summary
Severity: Critical
Advisory: GHSA-fr29-w6j4-525f
CVE: CVE-2023-41543
CWE: CWE-89
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-12-30
Source: https://github.com/advisories/GHSA-fr29-w6j4-525f
Type: github-advisory

## Affected
- Maven: `org.jeecgframework.boot:jeecg-boot-common` — affected >=0

## Details
SQL injection vulnerability in jeecg-boot v3.5.3, allows remote attackers to escalate privileges and obtain sensitive information via the component /sys/replicate/check.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-41543
- https://github.com/jeecgboot/jeecg-boot
- https://mp.weixin.qq.com/s/q6R-kaN4XS5d_cgWtq46vw
- https://pho3n1x-web.github.io/2023/09/18/CVE-2023-41543%28JeecgBoot_sql%29
