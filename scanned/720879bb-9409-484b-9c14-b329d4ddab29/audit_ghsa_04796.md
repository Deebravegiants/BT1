# [M] Spring Data Commons: StackOverflowException when parsing Sort parameters (DoS)

## Summary
Severity: Medium
Advisory: GHSA-5vpf-xvv7-c8vh
CVE: CVE-2026-41711
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-10
Source: https://github.com/advisories/GHSA-5vpf-xvv7-c8vh
Type: github-advisory

## Affected
- Maven: `org.springframework.data:spring-data-commons` — affected >=4.0.0 <4.0.6
- Maven: `org.springframework.data:spring-data-commons` — affected >=3.5.0 <3.5.12
- Maven: `org.springframework.data:spring-data-commons` — affected >=3.4.0
- Maven: `org.springframework.data:spring-data-commons` — affected >=3.0.0
- Maven: `org.springframework.data:spring-data-commons` — affected >=0

## Details
Applications using Spring Data Commons may be vulnerable to a Denial of Service (DoS) attack leading to a StackOverflowException when parsing Sort parameters.

Affected versions:
Spring Data Commons 4.0.0 through 4.0.5; 3.5.0 through 3.5.11; 3.4.0 through 3.4.14; 3.3.0 through 3.3.16; 3.2.0 through 3.2.15; 3.1.0 through 3.1.14; 3.0.0 through 3.0.15; 2.7.0 through 2.7.19.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-41711
- https://github.com/spring-projects/spring-data-commons
- https://github.com/spring-projects/spring-data-commons/releases/tag/3.5.12
- https://github.com/spring-projects/spring-data-commons/releases/tag/4.0.6
- https://spring.io/security/cve-2026-41711
