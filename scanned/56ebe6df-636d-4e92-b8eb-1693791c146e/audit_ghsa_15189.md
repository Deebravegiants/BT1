# [H] Spring Framework server Web DoS Vulnerability

## Summary
Severity: High
Advisory: GHSA-r4q3-7g4q-x89m
CVE: CVE-2024-22233
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-01-22
Source: https://github.com/advisories/GHSA-r4q3-7g4q-x89m
Type: github-advisory

## Affected
- Maven: `org.springframework:spring-core` — affected >=6.1.2 <6.1.3
- Maven: `org.springframework:spring-core` — affected >=6.0.15 <6.0.16

## Details
In Spring Framework versions 6.0.15 and 6.1.2, it is possible for a user to provide specially crafted HTTP requests that may cause a denial-of-service (DoS) condition.

Specifically, an application is vulnerable when all of the following are true:

  *  the application uses Spring MVC
  *  Spring Security 6.1.6+ or 6.2.1+ is on the classpath


Typically, Spring Boot applications need the org.springframework.boot:spring-boot-starter-web and org.springframework.boot:spring-boot-starter-security dependencies to meet all conditions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-22233
- https://security.netapp.com/advisory/ntap-20240614-0005
- https://spring.io/security/cve-2024-22233
