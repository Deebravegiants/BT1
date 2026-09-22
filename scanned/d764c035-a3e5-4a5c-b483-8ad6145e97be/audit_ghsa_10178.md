# [M] Spring Security has Potential Security Misconfiguration when Using withIssuerLocation

## Summary
Severity: Medium
Advisory: GHSA-cvc6-q2cp-2xhw
CVE: CVE-2026-22748
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-cvc6-q2cp-2xhw
Type: github-advisory

## Affected
- Maven: `org.springframework.security:spring-security-oauth2-jose` — affected >=6.3.0
- Maven: `org.springframework.security:spring-security-oauth2-jose` — affected >=6.4.0
- Maven: `org.springframework.security:spring-security-oauth2-jose` — affected >=6.5.0 <6.5.10
- Maven: `org.springframework.security:spring-security-oauth2-jose` — affected >=7.0.0 <7.0.5

## Details
Vulnerability in Spring Spring Security. When an application configures JWT decoding with NimbusJwtDecoder  or NimbusReactiveJwtDecoder, it must configure an OAuth2TokenValidator<Jwt> separately, for example by calling setJwtValidator. This issue affects Spring Security: from 6.3.0 through 6.3.14, from 6.4.0 through 6.4.14, from 6.5.0 through 6.5.9, from 7.0.0 through 7.0.4.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-22748
- https://github.com/spring-projects/spring-security
- https://spring.io/security/cve-2026-22748
