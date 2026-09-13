# [H] Spring Boot EndpointRequest.to() creates wrong matcher if actuator endpoint is not exposed

## Summary
Severity: High
Advisory: GHSA-rc42-6c7j-7h5r
CVE: CVE-2025-22235
CWE: CWE-20, CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2025-04-28
Source: https://github.com/advisories/GHSA-rc42-6c7j-7h5r
Type: github-advisory

## Affected
- Maven: `org.springframework.boot:spring-boot` — affected >=0
- Maven: `org.springframework.boot:spring-boot` — affected >=3.1.0
- Maven: `org.springframework.boot:spring-boot` — affected >=3.2.0
- Maven: `org.springframework.boot:spring-boot` — affected >=3.3.0 <3.3.11
- Maven: `org.springframework.boot:spring-boot` — affected >=3.4.0 <3.4.5

## Details
EndpointRequest.to() creates a matcher for null/** if the actuator endpoint, for which the EndpointRequest has been created, is disabled or not exposed.

Your application may be affected by this if all the following conditions are met:

  *  You use Spring Security
  *  EndpointRequest.to() has been used in a Spring Security chain configuration
  *  The endpoint which EndpointRequest references is disabled or not exposed via web
  *  Your application handles requests to /null and this path needs protection


You are not affected if any of the following is true:

  *  You don't use Spring Security
  *  You don't use EndpointRequest.to()
  *  The endpoint which EndpointRequest.to() refers to is enabled and is exposed
  *  Your application does not handle requests to /null or this path does not need protection

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-22235
- https://github.com/spring-projects/spring-boot
- https://security.netapp.com/advisory/ntap-20250516-0010
- https://spring.io/security/cve-2025-22235
