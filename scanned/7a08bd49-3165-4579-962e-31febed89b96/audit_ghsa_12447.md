# [C] JeecgBoot server-side template injection

## Summary
Severity: Critical
Advisory: GHSA-49jp-cghc-p5pj
CVE: CVE-2023-41544
CWE: CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2023-12-30
Source: https://github.com/advisories/GHSA-49jp-cghc-p5pj
Type: github-advisory

## Affected
- Maven: `org.jeecgframework.boot:jeecg-boot-common` — affected >=0

## Details
SSTI injection vulnerability in jeecg-boot version 3.5.3, allows remote attackers to execute arbitrary code via crafted HTTP request to the /jmreport/loadTableData component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-41544
- https://github.com/jeecgboot/jeecg-boot
- https://pho3n1x-web.github.io/2023/09/18/CVE-2023-41544%28JeecgBoot_SSTI%29
