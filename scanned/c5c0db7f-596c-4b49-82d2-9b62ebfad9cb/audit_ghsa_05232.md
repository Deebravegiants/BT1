# [H] Spring Security SAML2 Service Provider: Unbounded writer inflates the compressed SAML payload into memory (DoS)

## Summary
Severity: High
Advisory: GHSA-m69x-pw9p-7j3q
CVE: CVE-2026-40988
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-10
Source: https://github.com/advisories/GHSA-m69x-pw9p-7j3q
Type: github-advisory

## Affected
- Maven: `org.springframework.security:spring-security-saml2-service-provider` — affected >=7.0.0 <7.0.6
- Maven: `org.springframework.security:spring-security-saml2-service-provider` — affected >=6.5.0 <6.5.11
- Maven: `org.springframework.security:spring-security-saml2-service-provider` — affected >=6.4.0
- Maven: `org.springframework.security:spring-security-saml2-service-provider` — affected >=6.3.0
- Maven: `org.springframework.security:spring-security-saml2-service-provider` — affected >=5.8.0
- Maven: `org.springframework.security:spring-security-saml2-service-provider` — affected >=0

## Details
An application using spring-security-saml2-service-provider and the REDIRECT binding for SAML 2.0 Login or Logout may be vulnerable to a denial of service by way of an unbounded writer that inflates the compressed SAML payload into memory.

Affected versions:
Spring Security 5.7.0 through 5.7.23; 5.8.0 through 5.8.25; 6.3.0 through 6.3.16; 6.4.0 through 6.4.16; 6.5.0 through 6.5.10; 7.0.0 through 7.0.5.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-40988
- https://github.com/spring-projects/spring-security
- https://github.com/spring-projects/spring-security/releases/tag/6.5.11
- https://github.com/spring-projects/spring-security/releases/tag/7.0.6
- https://spring.io/security/cve-2026-40988
