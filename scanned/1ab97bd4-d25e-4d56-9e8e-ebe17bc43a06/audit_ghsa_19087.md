# [H] SQL injection in JeecgBoot

## Summary
Severity: High
Advisory: GHSA-wfpm-qchc-6cf9
CVE: CVE-2024-57606
CWE: CWE-200, CWE-89
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-02-08
Source: https://github.com/advisories/GHSA-wfpm-qchc-6cf9
Type: github-advisory

## Affected
- Maven: `org.jeecgframework.boot:jeecg-boot-common` — affected >=0 <3.7.3

## Details
SQL injection vulnerability in Beijing Guoju Information Technology Co., Ltd JeecgBoot v.3.7.2 allows a remote attacker to obtain sensitive information via the getTotalData component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-57606
- https://github.com/jeecgboot/JeecgBoot/issues/7665
