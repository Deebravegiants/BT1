# [H] Path traversal vulnerability in functional web frameworks

## Summary
Severity: High
Advisory: GHSA-cx7f-g6mp-7hqm
CVE: CVE-2024-38816
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-09-13
Source: https://github.com/advisories/GHSA-cx7f-g6mp-7hqm
Type: github-advisory

## Affected
- Maven: `org.springframework:spring-webmvc` — affected >=6.1.0 <6.1.13
- Maven: `org.springframework:spring-webflux` — affected >=6.1.0 <6.1.13
- Maven: `org.springframework:spring-webmvc` — affected >=6.0.0
- Maven: `org.springframework:spring-webflux` — affected >=6.0.0
- Maven: `org.springframework:spring-webmvc` — affected >=5.3.0
- Maven: `org.springframework:spring-webflux` — affected >=5.3.0

## Details
Applications serving static resources through the functional web frameworks WebMvc.fn or WebFlux.fn are vulnerable to path traversal attacks. An attacker can craft malicious HTTP requests and obtain any file on the file system that is also accessible to the process in which the Spring application is running.

Specifically, an application is vulnerable when both of the following are true:

  *  the web application uses RouterFunctions to serve static resources
  *  resource handling is explicitly configured with a FileSystemResource location


However, malicious requests are blocked and rejected when any of the following is true:

  *  the  Spring Security HTTP Firewall https://docs.spring.io/spring-security/reference/servlet/exploits/firewall.html  is in use
  *  the application runs on Tomcat or Jetty

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-38816
- https://github.com/spring-projects/spring-framework/commit/d86bf8b2056429edf5494456cffcb2b243331c49
- https://github.com/spring-projects/spring-framework
- https://security.netapp.com/advisory/ntap-20241227-0001
- https://spring.io/security/cve-2024-38816
