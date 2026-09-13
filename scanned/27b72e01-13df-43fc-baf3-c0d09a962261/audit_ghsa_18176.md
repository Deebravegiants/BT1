# [C] Spring Expression language property modification using Spring Cloud Gateway Server WebFlux

## Summary
Severity: Critical
Advisory: GHSA-q2cj-h8fw-q4cc
CVE: CVE-2025-41243
CWE: CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-09-16
Source: https://github.com/advisories/GHSA-q2cj-h8fw-q4cc
Type: github-advisory

## Affected
- Maven: `org.springframework.cloud:spring-cloud-gateway-server-webflux` — affected >=3.1.0
- Maven: `org.springframework.cloud:spring-cloud-gateway-server-webflux` — affected >=4.0.0
- Maven: `org.springframework.cloud:spring-cloud-gateway-server-webflux` — affected >=4.2.0 <4.2.5
- Maven: `org.springframework.cloud:spring-cloud-gateway-server-webflux` — affected >=4.3.0 <4.3.1

## Details
Spring Cloud Gateway Server Webflux may be vulnerable to Spring Environment property modification.

An application should be considered vulnerable when all the following are true:

  *  The application is using Spring Cloud Gateway Server Webflux (Spring Cloud Gateway Server WebMVC is not vulnerable).
  *  Spring Boot actuator is a dependency.
  *  The Spring Cloud Gateway Server Webflux actuator web endpoint is enabled via management.endpoints.web.exposure.include=gateway.
  *  The actuator endpoints are available to attackers.
  *  The actuator endpoints are unsecured.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-41243
- https://spring.io/security/cve-2025-41243
