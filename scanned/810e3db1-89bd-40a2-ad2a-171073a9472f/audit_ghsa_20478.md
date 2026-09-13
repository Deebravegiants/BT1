# [C] SQL Injection in JeecgBoot

## Summary
Severity: Critical
Advisory: GHSA-26hm-r6mg-963c
CVE: CVE-2021-46089
CWE: CWE-89
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-01-26
Source: https://github.com/advisories/GHSA-26hm-r6mg-963c
Type: github-advisory

## Affected
- Maven: `org.jeecgframework.boot:jeecg-boot-base` — affected >=0
- Maven: `org.jeecgframework.boot:jeecg-boot-base-core` — affected >=0

## Details
In JeecgBoot 3.0, there is a SQL injection vulnerability that can operate the database with root privileges. A patch has been released on the repository's `master` branch.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-46089
- https://github.com/jeecgboot/jeecg-boot/issues/3331
- https://github.com/jeecgboot/jeecg-boot/commit/baefc1338dd03de36384ce7d5846b08041b488d0
- https://github.com/jeecgboot/jeecg-boot
