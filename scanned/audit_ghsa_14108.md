# [H] Spring Boot Welcome Page Denial of Service

## Summary
Severity: High
Advisory: GHSA-xf96-w227-r7c4
CVE: CVE-2023-20883
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-05-26
Source: https://github.com/advisories/GHSA-xf96-w227-r7c4
Type: github-advisory

## Affected
- Maven: `org.springframework.boot:spring-boot-autoconfigure` — affected >=3.0.0 <3.0.7
- Maven: `org.springframework.boot:spring-boot-autoconfigure` — affected >=2.7.0 <2.7.12
- Maven: `org.springframework.boot:spring-boot-autoconfigure` — affected >=2.6.0 <2.6.15
- Maven: `org.springframework.boot:spring-boot-autoconfigure` — affected >=0 <2.5.15

## Details
In Spring Boot versions 3.0.0 - 3.0.6, 2.7.0 - 2.7.11, 2.6.0 - 2.6.14, 2.5.0 - 2.5.14 and older unsupported versions, there is potential for a denial-of-service (DoS) attack if Spring MVC is used together with a reverse proxy cache.

Specifically, an application is vulnerable if all of the conditions are true:

* The application has Spring MVC auto-configuration enabled. This is the case by default if Spring MVC is on the classpath.
* The application makes use of Spring Boot's welcome page support, either static or templated.
* Your application is deployed behind a proxy which caches 404 responses.

Your application is NOT vulnerable if any of the following are true:

* Spring MVC auto-configuration is disabled. This is true if WebMvcAutoConfiguration is explicitly excluded, if Spring MVC is not on the classpath, or if spring.main.web-application-type is set to a value other than SERVLET.
* The application does not use Spring Boot's welcome page support.
* You do not have a proxy which caches 404 responses.


Affected Spring Products and Versions

Spring Boot

3.0.0 to 3.0.6 2.7.0 to 2.7.11 2.6.0 to 2.6.14 2.5.0 to 2.5.14

Older, unsupported versions are also affected
Mitigation

Users of affected versions should apply the following mitigations:

* 3.0.x users should upgrade to 3.0.7+
* 2.7.x users should upgrade to 2.7.12+
* 2.6.x users should upgrade to 2.6.15+
* 2.5.x users should upgrade to 2.5.15+

Users of older, unsupported versions should upgrade to 3.0.7+ or 2.7.12+.

Workarounds: configure the reverse proxy not to cache 404 responses and/or not to cache responses to requests to the root (/) of the application.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-20883
- https://github.com/spring-projects/spring-boot/issues/35552
- https://github.com/spring-projects/spring-boot/commit/418dd1ba5bdad79b55a043000164bfcbda2acd78
- https://github.com/spring-projects/spring-boot
- https://github.com/spring-projects/spring-boot/releases/tag/v2.5.15
- https://github.com/spring-projects/spring-boot/releases/tag/v2.6.15
- https://github.com/spring-projects/spring-boot/releases/tag/v2.7.12
- https://security.netapp.com/advisory/ntap-20230703-0008
- https://spring.io/security/cve-2023-20883
