# [M] Log entry injection in Spring Framework

## Summary
Severity: Medium
Advisory: GHSA-6gf2-pvqw-37ph
CVE: CVE-2021-22060
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-01-12
Source: https://github.com/advisories/GHSA-6gf2-pvqw-37ph
Type: github-advisory

## Affected
- Maven: `org.springframework:spring-core` — affected >=5.3.0 <5.3.14
- Maven: `org.springframework:spring-core` — affected >=5.2.0 <5.2.19

## Details
In Spring Framework versions 5.3.0 - 5.3.13, 5.2.0 - 5.2.18, and older unsupported versions, it is possible for a user to provide malicious input to cause the insertion of additional log entries. This is a follow-up to CVE-2021-22096 that protects against additional types of input and in more places of the Spring Framework codebase.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-22060
- https://tanzu.vmware.com/security/cve-2021-22060
- https://www.oracle.com/security-alerts/cpuapr2022.html
