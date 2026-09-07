# [H] Hardcoded JWT Token in Lin CMS Spring Boot

## Summary
Severity: High
Advisory: GHSA-q72p-4w56-hx7h
CVE: CVE-2022-32430
CWE: CWE-668
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-07-22
Source: https://github.com/advisories/GHSA-q72p-4w56-hx7h
Type: github-advisory

## Affected
- Maven: `io.github.talelin:lin-cms-core` — affected >=0

## Details
An access control issue in Lin CMS Spring Boot v0.2.1 allows attackers to access the backend information and functions within the application.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-32430
- https://github.com/TaleLin/lin-cms-spring-boot
- https://github.com/TaleLin/lin-cms-spring-boot/blob/3fc25bd8c10c73db2e7230809b322127eac554e3/src/main/resources/application.yml#L43
- https://web.archive.org/web/20220721190946/https://www.mesec.cn/archives/277
