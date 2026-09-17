# [M] Spring Boot Actuator denial of service vulnerability

## Summary
Severity: Medium
Advisory: GHSA-jjfh-589g-3hjx
CVE: CVE-2023-34055
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2023-11-28
Source: https://github.com/advisories/GHSA-jjfh-589g-3hjx
Type: github-advisory

## Affected
- Maven: `org.springframework.boot:spring-boot-actuator` — affected >=0 <2.7.18
- Maven: `org.springframework.boot:spring-boot-actuator` — affected >=3.0.0 <3.0.13
- Maven: `org.springframework.boot:spring-boot-actuator` — affected >=3.1.0 <3.1.6

## Details
In Spring Boot versions 2.7.0 - 2.7.17, 3.0.0-3.0.12 and 3.1.0-3.1.5, it is possible for a user to provide specially crafted HTTP requests that may cause a denial-of-service (DoS) condition.

Specifically, an application is vulnerable when all of the following are true:

  *  the application uses Spring MVC or Spring WebFlux
  *  `org.springframework.boot:spring-boot-actuator` is on the classpath

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-34055
- https://github.com/spring-projects/spring-boot/commit/5490e73922b37a7f0bdde43eb318cb1038b45d60
- https://github.com/spring-projects/spring-boot
- https://security.netapp.com/advisory/ntap-20231221-0010
- https://security.snyk.io/vuln/SNYK-JAVA-ORGSPRINGFRAMEWORKBOOT-6226862
- https://spring.io/security/cve-2023-34055
