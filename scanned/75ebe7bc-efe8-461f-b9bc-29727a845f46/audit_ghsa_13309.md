# [H] Spring Security's authorization rules can be misconfigured when using multiple servlets

## Summary
Severity: High
Advisory: GHSA-4vpr-xfrp-cj64
CVE: CVE-2023-34035
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2023-07-18
Source: https://github.com/advisories/GHSA-4vpr-xfrp-cj64
Type: github-advisory

## Affected
- Maven: `org.springframework.security:spring-security-config` — affected >=5.8.0 <5.8.5
- Maven: `org.springframework.security:spring-security-config` — affected >=6.0.0 <6.0.5
- Maven: `org.springframework.security:spring-security-config` — affected >=6.1.0 <6.1.2

## Details
Spring Security versions 5.8 prior to 5.8.5, 6.0 prior to 6.0.5, and 6.1 prior to 6.1.2 could be susceptible to authorization rule misconfiguration if the application uses requestMatchers(String) and multiple servlets, one of them being Spring MVC’s DispatcherServlet. (DispatcherServlet is a Spring MVC component that maps HTTP endpoints to methods on @Controller-annotated classes.)

Specifically, an application is vulnerable when all of the following are true:

  *  Spring MVC is on the classpath
  *  Spring Security is securing more than one servlet in a single application (one of them being Spring MVC’s DispatcherServlet)
  *  The application uses requestMatchers(String) to refer to endpoints that are not Spring MVC endpoints


An application is not vulnerable if any of the following is true:

  *  The application does not have Spring MVC on the classpath
  *  The application secures no servlets other than Spring MVC’s DispatcherServlet
  *  The application uses requestMatchers(String) only for Spring MVC endpoints

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-34035
- https://github.com/spring-projects/spring-security-samples/commit/4e3bec904a5467db28ea33e25ac9d90524b53d66
- https://github.com/spring-projects/spring-security/commit/bb46a5427005e33e637b15948de8adae244ce547
- https://github.com/spring-projects/spring-security/commit/df239b6448ccf138b0c95b5575a88f33ac35cd9a
- https://github.com/spring-projects/spring-security-samples/tree/main/servlet/java-configuration/authentication/preauth
- https://spring.io/security/cve-2023-34035
