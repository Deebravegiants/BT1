# [M] Integer overflow in BCrypt class in Spring Security

## Summary
Severity: Medium
Advisory: GHSA-wx54-3278-m5g4
CVE: CVE-2022-22976
CWE: CWE-190
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-20
Source: https://github.com/advisories/GHSA-wx54-3278-m5g4
Type: github-advisory

## Affected
- Maven: `org.springframework.security:spring-security-core` — affected >=5.2.0.RELEASE <5.5.7
- Maven: `org.springframework.security:spring-security-core` — affected >=5.6.0 <5.6.4

## Details
Spring Security versions 5.5.x prior to 5.5.7, 5.6.x prior to 5.6.4, and earlier unsupported versions contain an integer overflow vulnerability. When using the BCrypt class with the maximum work factor (31), the encoder does not perform any salt rounds, due to an integer overflow error. The default settings are not affected by this CVE.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-22976
- https://github.com/spring-projects/spring-security/commit/388a7b62b906bd56deadb7ca45248fa1a63bdf12
- https://github.com/spring-projects/spring-security/commit/a40f73521c0dd88b879ff6165d280e78bdf8154f
- https://github.com/spring-projects/spring-security
- https://security.netapp.com/advisory/ntap-20220707-0003
- https://tanzu.vmware.com/security/cve-2022-22976
- https://www.oracle.com/security-alerts/cpujul2022.html
