# [M] Spring Framework MVC Applications Path Traversal Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-r936-gwx5-v52f
CVE: CVE-2025-41242
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-08-18
Source: https://github.com/advisories/GHSA-r936-gwx5-v52f
Type: github-advisory

## Affected
- Maven: `org.springframework:spring-webmvc` — affected >=6.2.0 <6.2.10
- Maven: `org.springframework:spring-webmvc` — affected >=6.1.0
- Maven: `org.springframework:spring-webmvc` — affected >=6.0.0
- Maven: `org.springframework:spring-webmvc` — affected >=5.3.0

## Details
Spring Framework MVC applications can be vulnerable to a “Path Traversal Vulnerability” when deployed on a non-compliant Servlet container.

An application can be vulnerable when all the following are true:

  *  the application is deployed as a WAR or with an embedded Servlet container
  *  the Servlet container  does not reject suspicious sequences https://jakarta.ee/specifications/servlet/6.1/jakarta-servlet-spec-6.1.html#uri-path-canonicalization 
  *  the application  serves static resources https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-config/static-resources.html#page-title  with Spring resource handling


We have verified that applications deployed on Apache Tomcat or Eclipse Jetty are not vulnerable, as long as default security features are not disabled in the configuration. Because we cannot check exploits against all Servlet containers and configuration variants, we strongly recommend upgrading your application.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-41242
- https://github.com/spring-projects/spring-framework
- http://spring.io/security/cve-2025-41242
