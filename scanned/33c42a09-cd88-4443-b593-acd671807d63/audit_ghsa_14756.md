# [M] Spring Framework has Authorization Bypass for Case Sensitive Comparisons

## Summary
Severity: Medium
Advisory: GHSA-q3v6-hm2v-pw99
CVE: CVE-2024-38827
CWE: CWE-639
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-12-02
Source: https://github.com/advisories/GHSA-q3v6-hm2v-pw99
Type: github-advisory

## Affected
- Maven: `org.springframework.security:spring-security-core` — affected >=0 <5.7.14
- Maven: `org.springframework.security:spring-security-core` — affected >=5.8.0 <5.8.16
- Maven: `org.springframework.security:spring-security-core` — affected >=6.0.0 <6.0.14
- Maven: `org.springframework.security:spring-security-core` — affected >=6.1.0 <6.1.12
- Maven: `org.springframework.security:spring-security-core` — affected >=6.2.0 <6.2.8
- Maven: `org.springframework.security:spring-security-core` — affected >=6.3.0 <6.3.5

## Details
The usage of String.toLowerCase() and String.toUpperCase() has some Locale dependent exceptions that could potentially result in authorization rules not working properly.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-38827
- https://github.com/spring-projects/spring-framework/issues/33708
- https://github.com/spring-projects/spring-framework/issues/34232
- https://github.com/spring-projects/spring-framework/commit/11d4272ff48b4a4dabc4b28dfbff0364a4204bc9
- https://github.com/spring-projects/spring-security
- https://security.netapp.com/advisory/ntap-20250124-0007
- https://spring.io/security/cve-2024-38827
