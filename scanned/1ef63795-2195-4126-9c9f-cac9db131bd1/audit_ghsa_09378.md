# [M] Spring Cloud Config Server Logged Sensitive Information

## Summary
Severity: Medium
Advisory: GHSA-j6hh-h3cf-c2hf
CVE: CVE-2026-41004
CWE: CWE-532
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-j6hh-h3cf-c2hf
Type: github-advisory

## Affected
- Maven: `org.springframework.cloud:spring-cloud-config-server` — affected >=3.1.0
- Maven: `org.springframework.cloud:spring-cloud-config-server` — affected >=4.1.0
- Maven: `org.springframework.cloud:spring-cloud-config-server` — affected >=4.2.0
- Maven: `org.springframework.cloud:spring-cloud-config-server` — affected >=4.3.0 <4.3.3
- Maven: `org.springframework.cloud:spring-cloud-config-server` — affected >=5.0.0 <5.0.3
- Maven: `org.springframework.cloud:spring-cloud-config-server` — affected >=3.0.0

## Details
When trace logging is enabled in Spring Cloud Config Server, sensitive information is placed in plain text in the logs.

- Spring Cloud Config 3.0.x: affected from 3.0.0 through 3.0.7 (inclusive); no open-source upgrade available.
- Spring Cloud Config 3.1.x: affected from 3.1.0 through 3.1.13 (inclusive); no open-source upgrade available.
- Spring Cloud Config 4.1.x: affected from 4.1.0 through 4.1.9 (inclusive); no open-source upgrade available.
- Spring Cloud Config 4.2.x: affected from 4.2.0 through 4.2.6 (inclusive); no open-source upgrade available.
- Spring Cloud Config 4.3.x: affected from 4.3.0 through 4.3.2 (inclusive); upgrade to 4.3.3 or greater.
- Spring Cloud Config 5.0.x: affected from 5.0.0 through 5.0.2 (inclusive); upgrade to 5.0.3 or greater.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-41004
- https://github.com/spring-cloud/spring-cloud-config
- https://spring.io/security/cve-2026-41004
