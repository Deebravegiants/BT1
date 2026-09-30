# [C] Spring Security authorization bypass for method security annotations on private methods

## Summary
Severity: Critical
Advisory: GHSA-9pp5-9c7g-4r83
CVE: CVE-2025-41232
CWE: CWE-693
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-05-21
Source: https://github.com/advisories/GHSA-9pp5-9c7g-4r83
Type: github-advisory

## Affected
- Maven: `org.springframework.security:spring-security-aspects` — affected >=6.4.0 <6.4.6
- Maven: `org.springframework.security:spring-security-core` — affected >=6.4.0 <6.4.6

## Details
Spring Security Aspects may not correctly locate method security annotations on private methods. This can cause an authorization bypass.

Your application may be affected by this if the following are true:

  *  You are using @EnableMethodSecurity(mode=ASPECTJ) and spring-security-aspects, and
  *  You have Spring Security method annotations on a private method
In that case, the target method may be able to be invoked without proper authorization.

You are not affected if:

  *  You are not using @EnableMethodSecurity(mode=ASPECTJ) or spring-security-aspects, or
  *  You have no Spring Security-annotated private methods

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-41232
- https://github.com/spring-projects/spring-security/commit/bf2aaa1b1830e534ba651d422545ac08a115151b
- https://github.com/spring-projects/spring-security/commit/c972de5369a1261ab674a3f5e3a80e8ce3e8cdfb
- https://github.com/spring-projects/spring-security
- https://github.com/spring-projects/spring-security/releases/tag/6.4.6
- http://spring.io/security/cve-2025-41232
