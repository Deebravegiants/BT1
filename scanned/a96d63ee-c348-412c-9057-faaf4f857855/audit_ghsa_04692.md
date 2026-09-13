# [H] Spring Cloud Sleuth instrumentation of Spring TX DoS vulnerability

## Summary
Severity: High
Advisory: GHSA-26m2-9g2q-v45q
CVE: CVE-2026-41708
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-26m2-9g2q-v45q
Type: github-advisory

## Affected
- Maven: `org.springframework.cloud:spring-cloud-sleuth-instrumentation` — affected >=3.1.0

## Details
In Spring Cloud Sleuth, it is possible for a user to provide specially crafted calls that may cause a denial-of-service (DoS) condition. The application is vulnerable when it uses a vulnerable version of org.springframework.cloud:spring-cloud-sleuth-instrumentation and Spring TX instrumentation is not disabled.

Affected versions:
Spring Cloud Sleuth 3.1.0 through 3.1.13.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-41708
- https://github.com/spring-attic/spring-cloud-sleuth
- https://spring.io/security/cve-2026-41708
