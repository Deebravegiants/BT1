# [H] Spring Cloud Config has an Authorization Bypass Through User-Controlled Key 

## Summary
Severity: High
Advisory: GHSA-2mh5-3cw6-hrrq
CVE: CVE-2026-40981
CWE: CWE-639
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-2mh5-3cw6-hrrq
Type: github-advisory

## Affected
- Maven: `org.springframework.cloud:spring-cloud-config-server` — affected >=3.1.0
- Maven: `org.springframework.cloud:spring-cloud-config-server` — affected >=4.1.0
- Maven: `org.springframework.cloud:spring-cloud-config-server` — affected >=4.2.0
- Maven: `org.springframework.cloud:spring-cloud-config-server` — affected >=4.3.0 <4.3.3
- Maven: `org.springframework.cloud:spring-cloud-config-server` — affected >=5.0.0 <5.0.3

## Details
When using Google Secrets Manager as a backend for the Spring Cloud Config server a client can craft a request to the config server potentially exposing secrets from unintended GCP projects.
Spring Cloud Config 3.1.x: affected from 3.1.0 through 3.1.13 (inclusive); upgrade to 3.1.14 or greater (Enterprise Support Only). Spring Cloud Config 4.1.x: affected from 4.1.0 through 4.1.9 (inclusive); upgrade to 4.1.10 or greater (Enterprise Support Only). Spring Cloud Config 4.2.x: affected from 4.2.0 through 4.2.6 (inclusive); upgrade to 4.2.7 or greater (Enterprise Support Only). Spring Cloud Config 4.3.x: affected from 4.3.0 through 4.3.2 (inclusive); upgrade to 4.3.3 or greater. Spring Cloud Config 5.0.x: affected from 5.0.0 through 5.0.2 (inclusive); upgrade to 5.0.3 or greater.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-40981
- https://github.com/spring-cloud/spring-cloud-config
- https://spring.io/security/cve-2026-40981
