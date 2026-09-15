# [M] Spring MVC and WebFlux applications are vulnerable to Denial of Service attacks when resolving static resources

## Summary
Severity: Medium
Advisory: GHSA-6p4f-wcwh-5vvm
CVE: CVE-2026-22745
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-04-29
Source: https://github.com/advisories/GHSA-6p4f-wcwh-5vvm
Type: github-advisory

## Affected
- Maven: `org.springframework:spring-webflux` — affected >=7.0.0 <7.0.7
- Maven: `org.springframework:spring-webflux` — affected >=6.2.0 <6.2.18
- Maven: `org.springframework:spring-webflux` — affected >=6.1.0
- Maven: `org.springframework:spring-webflux` — affected >=0
- Maven: `org.springframework:spring-webmvc` — affected >=7.0.0 <7.0.7
- Maven: `org.springframework:spring-webmvc` — affected >=6.2.0 <6.2.18
- Maven: `org.springframework:spring-webmvc` — affected >=6.1.0
- Maven: `org.springframework:spring-webmvc` — affected >=0

## Details
Spring MVC and WebFlux applications are vulnerable to Denial of Service attacks when resolving static resources.


More precisely, an application can be vulnerable when all the following are true:

  *  the application is using Spring MVC or Spring WebFlux
  *  the application is serving static resources from the file system
  *  the application is running on a Windows platform


When all the conditions above are met, the attacker can send malicious requests that are slow to resolve and that can keep HTTP connections in use. This can cause a Denial of Service on the application.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-22745
- https://github.com/spring-projects/spring-framework
- https://spring.io/security/cve-2026-22745
