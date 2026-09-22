# [C] Spring Framework is vulnerable to security bypass via mvcRequestMatcher pattern mismatch

## Summary
Severity: Critical
Advisory: GHSA-7phw-cxx7-q9vq
CVE: CVE-2023-20860
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2023-03-28
Source: https://github.com/advisories/GHSA-7phw-cxx7-q9vq
Type: github-advisory

## Affected
- Maven: `org.springframework:spring` — affected >=6.0.0 <6.0.7
- Maven: `org.springframework:spring` — affected >=5.3.0 <5.3.26
- Maven: `org.springframework:spring-webmvc` — affected >=6.0.0 <6.0.7
- Maven: `org.springframework:spring-webmvc` — affected >=5.3.0 <5.3.26

## Details
Spring Framework running version 6.0.0 - 6.0.6 or 5.3.0 - 5.3.25 using "**" as a pattern in Spring Security configuration with the mvcRequestMatcher creates a mismatch in pattern matching between Spring Security and Spring MVC, and the potential for a security bypass.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-20860
- https://github.com/spring-projects/spring-framework/commit/202fa5cdb3a3d0cfe6967e85fa167d978244f28a
- https://github.com/spring-projects/spring-framework
- https://security.netapp.com/advisory/ntap-20230505-0006
- https://spring.io/security/cve-2023-20860
