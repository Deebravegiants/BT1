# [M] JeecgBoot vulnerable to SQL injection in queryTableDictItemsByCode

## Summary
Severity: Medium
Advisory: GHSA-784x-7w88-w564
CVE: CVE-2023-34602
CWE: CWE-89
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-06-19
Source: https://github.com/advisories/GHSA-784x-7w88-w564
Type: github-advisory

## Affected
- Maven: `org.jeecgframework.boot:jeecg-boot-parent` — affected >=0 <3.5.1

## Details
JeecgBoot up to v 3.5.1 was discovered to contain a SQL injection vulnerability via the component `queryTableDictItemsByCode` in method `org.jeecg.modules.api.controller.SystemApiController`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-34602
- https://github.com/jeecgboot/jeecg-boot/issues/4983
- https://github.com/jeecgboot/jeecg-boot/commit/dd7bf104e7ed59142909567ecd004335c3442ec5
- https://github.com/jeecgboot/jeecg-boot
