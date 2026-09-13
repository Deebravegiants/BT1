# [C] Spring Security vulnerable to Authorization Bypass of Static Resources in WebFlux Applications

## Summary
Severity: Critical
Advisory: GHSA-c4q5-6c82-3qpw
CVE: CVE-2024-38821
CWE: CWE-285, CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-10-28
Source: https://github.com/advisories/GHSA-c4q5-6c82-3qpw
Type: github-advisory

## Affected
- Maven: `org.springframework.security:spring-security-web` — affected >=5.0.0 <5.7.13
- Maven: `org.springframework.security:spring-security-web` — affected >=5.8.0 <5.8.15
- Maven: `org.springframework.security:spring-security-web` — affected >=6.2.0 <6.2.7
- Maven: `org.springframework.security:spring-security-web` — affected >=6.0.0 <6.0.13
- Maven: `org.springframework.security:spring-security-web` — affected >=6.1.0 <6.1.11
- Maven: `org.springframework.security:spring-security-web` — affected >=6.3.0 <6.3.4

## Details
Spring WebFlux applications that have Spring Security authorization rules on static resources can be bypassed under certain circumstances.

For this to impact an application, all of the following must be true:

  *  It must be a WebFlux application
  *  It must be using Spring's static resources support
  *  It must have a non-permitAll authorization rule applied to the static resources support

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-38821
- https://github.com/spring-projects/spring-security/commit/0e257b56ce35402558a260ffa6b368982f9a7934
- https://github.com/spring-projects/spring-security/commit/4ce7cde15599c0447163fd46bac616e03318bf5b
- https://github.com/spring-projects/spring-security/commit/b4f27777556c157ec5689c0769322c90be984514
- https://github.com/spring-projects/spring-security
- https://security.netapp.com/advisory/ntap-20250124-0006
- https://spring.io/security/cve-2024-38821
