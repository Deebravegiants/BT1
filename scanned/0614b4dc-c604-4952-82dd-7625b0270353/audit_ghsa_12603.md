# [M] JeecgBoot vulnerable to SQL injection in queryFilterTableDictInfo

## Summary
Severity: Medium
Advisory: GHSA-cvgc-465m-cw9g
CVE: CVE-2023-34603
CWE: CWE-89
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-06-19
Source: https://github.com/advisories/GHSA-cvgc-465m-cw9g
Type: github-advisory

## Affected
- Maven: `org.jeecgframework.boot:jeecg-boot-parent` — affected >=0 <3.5.1

## Details
JeecgBoot up to v 3.5.1 was discovered to contain a SQL injection vulnerability via the component `queryFilterTableDictInfo` in method `org.jeecg.modules.api.controller.SystemApiController`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-34603
- https://github.com/jeecgboot/jeecg-boot/issues/4984
- https://github.com/jeecgboot/jeecg-boot
