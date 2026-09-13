# [C] Remote Code Execution in Spring Framework

## Summary
Severity: Critical
Advisory: GHSA-36p3-wjmg-h94x
CVE: CVE-2022-22965
CWE: CWE-74, CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H/E:H (CVSS_V3)
Published: 2022-03-31
Source: https://github.com/advisories/GHSA-36p3-wjmg-h94x
Type: github-advisory

## Affected
- Maven: `org.springframework:spring-beans` — affected >=0 <5.2.20.RELEASE
- Maven: `org.springframework:spring-beans` — affected >=5.3.0 <5.3.18
- Maven: `org.springframework:spring-webmvc` — affected >=0 <5.2.20.RELEASE
- Maven: `org.springframework:spring-webmvc` — affected >=5.3.0 <5.3.18
- Maven: `org.springframework.boot:spring-boot-starter-web` — affected >=0 <2.5.12
- Maven: `org.springframework.boot:spring-boot-starter-web` — affected >=2.6.0 <2.6.6
- Maven: `org.springframework:spring-webflux` — affected >=0 <5.2.20.RELEASE
- Maven: `org.springframework:spring-webflux` — affected >=5.3.0 <5.3.18
- Maven: `org.springframework.boot:spring-boot-starter-webflux` — affected >=0 <2.5.12
- Maven: `org.springframework.boot:spring-boot-starter-webflux` — affected >=2.6.0 <2.6.6

## Details
Spring Framework prior to versions 5.2.20 and 5.3.18 contains a remote code execution vulnerability known as `Spring4Shell`. 

## Impact

A Spring MVC or Spring WebFlux application running on JDK 9+ may be vulnerable to remote code execution (RCE) via data binding. The specific exploit requires the application to run on Tomcat as a WAR deployment. If the application is deployed as a Spring Boot executable jar, i.e. the default, it is not vulnerable to the exploit. However, the nature of the vulnerability is more general, and there may be other ways to exploit it.

These are the prerequisites for the exploit:
- JDK 9 or higher
- Apache Tomcat as the Servlet container
- Packaged as WAR
- `spring-webmvc` or `spring-webflux` dependency

## Patches

- Spring Framework [5.3.18](https://github.com/spring-projects/spring-framework/releases/tag/v5.3.18) and [5.2.20](https://github.com/spring-projects/spring-framework/releases/tag/v5.2.20.RELEASE)
- Spring Boot [2.6.6](https://github.com/spring-projects/spring-boot/releases/tag/v2.6.6) and [2.5.12](https://github.com/spring-projects/spring-boot/releases/tag/v2.5.12)

## Workarounds

For those who are unable to upgrade, leaked reports recommend setting `disallowedFields` on `WebDataBinder` through an `@ControllerAdvice`. This works generally, but as a centrally applied workaround fix, may leave some loopholes, in particular if a controller sets `disallowedFields` locally through its own `@InitBinder` method, which overrides the global setting.

To apply the workaround in a more fail-safe way, applications could extend `RequestMappingHandlerAdapter` to update the `WebDataBinder` at the end after all other initialization. In order to do that, a Spring Boot application can declare a `WebMvcRegistrations` bean (Spring MVC) or a `WebFluxRegistrations` bean (Spring WebFlux).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-22965
- https://github.com/spring-projects/spring-framework/commit/002546b3e4b8d791ea6acccb81eb3168f51abb15
- https://cert-portal.siemens.com/productcert/pdf/ssa-254054.pdf
- https://github.com/spring-projects/spring-boot/releases/tag/v2.5.12
- https://github.com/spring-projects/spring-boot/releases/tag/v2.6.6
- https://github.com/spring-projects/spring-framework
- https://github.com/spring-projects/spring-framework/releases/tag/v5.2.20.RELEASE
- https://github.com/spring-projects/spring-framework/releases/tag/v5.3.18
- https://psirt.global.sonicwall.com/vuln-detail/SNWLID-2022-0005
- https://spring.io/blog/2022/03/31/spring-framework-rce-early-announcement
- https://tanzu.vmware.com/security/cve-2022-22965
- https://tools.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-java-spring-rce-Zx9GUc67
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2022-22965
- https://www.kb.cert.org/vuls/id/970766
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpujul2022.html
- http://packetstormsecurity.com/files/166713/Spring4Shell-Code-Execution.html
- http://packetstormsecurity.com/files/167011/Spring4Shell-Spring-Framework-Class-Property-Remote-Code-Execution.html
