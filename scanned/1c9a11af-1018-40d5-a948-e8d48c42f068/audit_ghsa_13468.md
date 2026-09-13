# [C] Access Control Bypass in Spring Security

## Summary
Severity: Critical
Advisory: GHSA-3h6f-g5f3-gc4w
CVE: CVE-2023-34034
CWE: CWE-281, CWE-284
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2023-07-19
Source: https://github.com/advisories/GHSA-3h6f-g5f3-gc4w
Type: github-advisory

## Affected
- Maven: `org.springframework.security:spring-security-config` — affected >=5.6.0 <5.6.12
- Maven: `org.springframework.security:spring-security-config` — affected >=5.7.0 <5.7.10
- Maven: `org.springframework.security:spring-security-config` — affected >=5.8.0 <5.8.5
- Maven: `org.springframework.security:spring-security-config` — affected >=6.0.0 <6.0.5
- Maven: `org.springframework.security:spring-security-config` — affected >=6.1.0 <6.1.2

## Details
Using "**" as a pattern in Spring Security configuration for WebFlux creates a mismatch in pattern matching between Spring Security and Spring WebFlux, and the potential for a security bypass.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-34034
- https://ossindex.sonatype.org/vulnerability/CVE-2023-34034
- https://security.netapp.com/advisory/ntap-20230814-0008
- https://security.snyk.io/vuln/SNYK-JAVA-ORGSPRINGFRAMEWORKSECURITY-5777893
- https://spring.io/security/cve-2023-34034
