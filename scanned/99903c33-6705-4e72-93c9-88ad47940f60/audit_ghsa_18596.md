# [H] Spring Cloud Gateway Server Webflux is vulnerable to Expression Language Injection

## Summary
Severity: High
Advisory: GHSA-fwxx-wv44-7qfg
CVE: CVE-2025-41253
CWE: CWE-917
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-10-16
Source: https://github.com/advisories/GHSA-fwxx-wv44-7qfg
Type: github-advisory

## Affected
- Maven: `org.springframework.cloud:spring-cloud-gateway-server` — affected >=4.3.0 <4.3.2
- Maven: `org.springframework.cloud:spring-cloud-gateway-server` — affected >=4.2.0 <4.2.6
- Maven: `org.springframework.cloud:spring-cloud-gateway-server` — affected >=4.0.0
- Maven: `org.springframework.cloud:spring-cloud-gateway-server` — affected >=0

## Details
The following versions of Spring Cloud Gateway Server Webflux may be vulnerable to the ability to expose environment variables and system properties to attackers.

An application should be considered vulnerable when all the following are true:

  *  The application is using Spring Cloud Gateway Server Webflux (Spring Cloud Gateway Server WebMVC is not vulnerable).
  *  An admin or untrusted third party using Spring Expression Language (SpEL) to access environment variables or system properties via routes.
  *  An untrusted third party could create a route that uses SpEL to access environment variables or system properties if:  *  The Spring Cloud Gateway Server Webflux actuator web endpoint is enabled via management.endpoints.web.exposure.include=gateway and management.endpoint.gateway.enabled=trueor management.endpoint.gateway.access=unrestricte.
  *  The actuator endpoints are available to attackers.
  *  The actuator endpoints are unsecured.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-41253
- https://github.com/spring-cloud/spring-cloud-gateway
- https://nvd.nist.gov/vuln-metrics/cvss/v3-calculator?vector=AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N&version=3.1
- https://spring.io/security/cve/2025-41253
- https://www.cve.org/CVERecord?id=CVE-2025-41253
