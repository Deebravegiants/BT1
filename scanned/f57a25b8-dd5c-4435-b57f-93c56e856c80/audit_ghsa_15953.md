# [H] JeecgBoot SQL Injection vulnerability

## Summary
Severity: High
Advisory: GHSA-mcw3-h5xg-r95m
CVE: CVE-2024-48307
CWE: CWE-89
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-10-31
Source: https://github.com/advisories/GHSA-mcw3-h5xg-r95m
Type: github-advisory

## Affected
- Maven: `org.jeecgframework.boot:jeecg-boot-parent` — affected >=0

## Details
JeecgBoot v3.7.1 was discovered to contain a SQL injection vulnerability via the component `/onlDragDatasetHead/getTotalData`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-48307
- https://github.com/jeecgboot/JeecgBoot/issues/7237
- https://github.com/jeecgboot
- https://github.com/jeecgboot/JeecgBoot
