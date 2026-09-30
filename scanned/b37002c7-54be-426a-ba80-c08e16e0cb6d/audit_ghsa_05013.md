# [M] Spring Cloud Function Context: Uncontrolled Recursion is possible while attempting to add infinite amount of functions to Function Registry

## Summary
Severity: Medium
Advisory: GHSA-x4h3-g2x4-8gqv
CVE: CVE-2026-40990
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:P/AC:L/PR:L/UI:R/S:C/C:N/I:L/A:H (CVSS_V3)
Published: 2026-06-01
Source: https://github.com/advisories/GHSA-x4h3-g2x4-8gqv
Type: github-advisory

## Affected
- Maven: `org.springframework.cloud:spring-cloud-function-context` — affected >=4.3.0 <4.3.3
- Maven: `org.springframework.cloud:spring-cloud-function-context` — affected >=5.0.0 <5.0.2
- Maven: `org.springframework.cloud:spring-cloud-function-context` — affected >=3.2.10
- Maven: `org.springframework.cloud:spring-cloud-function-context` — affected >=4.1.0
- Maven: `org.springframework.cloud:spring-cloud-function-context` — affected >=4.2.0

## Details
OOM error is possible while attempting to add infinite amount of functions to Function Registry.

Affected Spring Products and Versions:
Spring Cloud Function 3.2.x: versions prior to 3.2.16
Spring Cloud Function 4.1.x: versions prior to 4.1.10
Spring Cloud Function 4.2.x: versions prior to 4.2.6
Spring Cloud Function 4.3.x: versions prior to 4.3.3
Spring Cloud Function 5.0.x: versions prior to 5.0.2
Older, unsupported versions are also affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-40990
- https://spring.io/security/cve-2026-40990
