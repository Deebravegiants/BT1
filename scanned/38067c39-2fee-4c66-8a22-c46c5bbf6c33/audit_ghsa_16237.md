# [H] Broken Access Control in Spring Security With Direct Use of isFullyAuthenticated

## Summary
Severity: High
Advisory: GHSA-w3w6-26f2-p474
CVE: CVE-2024-22234
CWE: CWE-284
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-02-20
Source: https://github.com/advisories/GHSA-w3w6-26f2-p474
Type: github-advisory

## Affected
- Maven: `org.springframework.security:spring-security-core` — affected >=6.1.0 <6.1.7
- Maven: `org.springframework.security:spring-security-core` — affected >=6.2.0 <6.2.2

## Details
In Spring Security, versions 6.1.x prior to 6.1.7 and versions 6.2.x prior to 6.2.2, an application is vulnerable to broken access control when it directly uses the AuthenticationTrustResolver.isFullyAuthenticated(Authentication) method.

Specifically, an application is vulnerable if:

  *  The application uses AuthenticationTrustResolver.isFullyAuthenticated(Authentication) directly and a null authentication parameter is passed to it resulting in an erroneous true return value.


An application is not vulnerable if any of the following is true:

  *  The application does not use AuthenticationTrustResolver.isFullyAuthenticated(Authentication) directly.
  *  The application does not pass null to AuthenticationTrustResolver.isFullyAuthenticated
  *  The application only uses isFullyAuthenticated via  Method Security https://docs.spring.io/spring-security/reference/servlet/authorization/method-security.html  or  HTTP Request Security https://docs.spring.io/spring-security/reference/servlet/authorization/authorize-http-requests.html

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-22234
- https://github.com/spring-projects/spring-security/commit/750cb30ce44d279c2f54c845d375e6a58bded569
- https://github.com/spring-projects/spring-security
- https://security.netapp.com/advisory/ntap-20240315-0003
- https://spring.io/security/cve-2024-22234
