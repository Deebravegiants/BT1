# [H] Spring Cloud Function Framework vulnerable to Denial of Service

## Summary
Severity: High
Advisory: GHSA-j4r7-p9fp-w3f3
CVE: CVE-2024-22271
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H (CVSS_V3)
Published: 2024-07-09
Source: https://github.com/advisories/GHSA-j4r7-p9fp-w3f3
Type: github-advisory

## Affected
- Maven: `org.springframework.cloud:spring-cloud-function-context` — affected >=4.0.0 <4.0.8
- Maven: `org.springframework.cloud:spring-cloud-function-context` — affected >=4.1.0 <4.1.2

## Details
In Spring Cloud Function framework, versions 4.1.x prior to 4.1.2, 4.0.x prior to 4.0.8 an application is vulnerable to a DOS attack when attempting to compose functions with non-existing functions.

Specifically, an application is vulnerable when all of the following are true:

User is using Spring Cloud Function Web module

Affected Spring Products and Versions Spring Cloud Function Framework 4.1.0 to 4.1.2 4.0.0 to 4.0.8

References  https://spring.io/security/cve-2022-22979   https://checkmarx.com/blog/spring-function-cloud-dos-cve-2022-22979-and-unintended-function-invocation/  History 2020-01-16: Initial vulnerability report published.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-22271
- https://github.com/spring-cloud/spring-cloud-function/issues/1139
- https://github.com/spring-cloud/spring-cloud-function/commit/59fe298b67fcb9249db727a7b3a33612fc7a9f75
- https://github.com/spring-cloud/spring-cloud-function
- https://github.com/spring-cloud/spring-cloud-function/releases/tag/v4.1.2
- https://spring.io/security/cve-2024-22271
