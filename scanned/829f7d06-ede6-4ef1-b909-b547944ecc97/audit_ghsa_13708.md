# [H] Spring Framework vulnerable to denial of service

## Summary
Severity: High
Advisory: GHSA-v94h-hvhg-mf9h
CVE: CVE-2023-34053
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-11-28
Source: https://github.com/advisories/GHSA-v94h-hvhg-mf9h
Type: github-advisory

## Affected
- Maven: `org.springframework:spring-webmvc` — affected >=6.0.0 <6.0.14

## Details
In Spring Framework versions 6.0.0 - 6.0.13, it is possible for a user to provide specially crafted HTTP requests that may cause a denial-of-service (DoS) condition.

Specifically, an application is vulnerable when all of the following are true:

  *  the application uses Spring MVC or Spring WebFlux
  *  io.micrometer:micrometer-core is on the classpath
  *  an ObservationRegistry is configured in the application to record observations


Typically, Spring Boot applications need the org.springframework.boot:spring-boot-actuator dependency to meet all conditions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-34053
- https://github.com/spring-projects/spring-framework/commit/c18784678df489d06a70e54fcddb5e3821d4b00c
- https://github.com/spring-projects/spring-framework
- https://github.com/spring-projects/spring-framework/compare/v6.0.13...v6.0.14
- https://security.netapp.com/advisory/ntap-20231214-0007
- https://spring.io/security/cve-2023-34053
