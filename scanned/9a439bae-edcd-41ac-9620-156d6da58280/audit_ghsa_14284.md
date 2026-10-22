# [C] Spring Boot Security Bypass with Wildcard Pattern Matching on Cloud Foundry

## Summary
Severity: Critical
Advisory: GHSA-g5h3-w546-pj7f
CVE: CVE-2023-20873
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-04-20
Source: https://github.com/advisories/GHSA-g5h3-w546-pj7f
Type: github-advisory

## Affected
- Maven: `org.springframework.boot:spring-boot-actuator-autoconfigure` — affected >=3.0.0 <3.0.6
- Maven: `org.springframework.boot:spring-boot-actuator-autoconfigure` — affected >=2.7.0 <2.7.11
- Maven: `org.springframework.boot:spring-boot-actuator-autoconfigure` — affected >=2.6.0 <2.6.15
- Maven: `org.springframework.boot:spring-boot-actuator-autoconfigure` — affected >=0 <2.5.15

## Details
In Spring Boot versions 3.0.0 - 3.0.5, 2.7.0 - 2.7.10, and older unsupported versions, an application that is deployed to Cloud Foundry could be susceptible to a security bypass. Users of affected versions should apply the following mitigation: 3.0.x users should upgrade to 3.0.6+. 2.7.x users should upgrade to 2.7.11+. Users of older, unsupported versions should upgrade to 3.0.6+ or 2.7.11+.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-20873
- https://github.com/spring-projects/spring-boot/commit/32444fed4b51cc58dc908467f706102d7f0bfc15
- https://github.com/spring-projects/spring-boot/commit/3522714c13b47af03bf42e7f2d5994af568cb1a7
- https://github.com/spring-projects/spring-boot
- https://github.com/spring-projects/spring-boot/releases/tag/v2.5.15
- https://github.com/spring-projects/spring-boot/releases/tag/v2.6.15
- https://github.com/spring-projects/spring-boot/releases/tag/v2.7.11
- https://github.com/spring-projects/spring-boot/releases/tag/v3.0.6
- https://security.netapp.com/advisory/ntap-20230601-0009
- https://spring.io/blog/2023/05/18/spring-boot-2-5-15-and-2-6-15-available-now
- https://spring.io/security/cve-2023-20873
