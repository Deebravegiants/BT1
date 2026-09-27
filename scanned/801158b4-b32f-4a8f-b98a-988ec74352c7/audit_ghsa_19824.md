# [H] Spring Security Does Not Enforce Password Length

## Summary
Severity: High
Advisory: GHSA-mg83-c7gq-rv5c
CVE: CVE-2025-22228
CWE: CWE-287, CWE-521
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-mg83-c7gq-rv5c
Type: github-advisory

## Affected
- Maven: `org.springframework.security:spring-security-crypto` — affected >=6.3.0 <6.3.8
- Maven: `org.springframework.security:spring-security-crypto` — affected >=6.4.0 <6.4.4
- Maven: `org.springframework.security:spring-security-crypto` — affected >=6.2.0 <6.2.10
- Maven: `org.springframework.security:spring-security-crypto` — affected >=6.1.0 <6.1.14
- Maven: `org.springframework.security:spring-security-crypto` — affected >=6.0.0 <6.0.16
- Maven: `org.springframework.security:spring-security-crypto` — affected >=5.8.0 <5.8.18
- Maven: `org.springframework.security:spring-security-crypto` — affected >=0 <5.7.16

## Details
BCryptPasswordEncoder.matches(CharSequence,String) will incorrectly return true for passwords larger than 72 characters as long as the first 72 characters are the same.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-22228
- https://github.com/spring-projects/spring-security/commit/46f0dc6dfc8402cd556c598fdf2d31f9d46cdbf3
- https://github.com/spring-projects/spring-security
- https://security.netapp.com/advisory/ntap-20250425-0009
- https://spring.io/security/cve-2025-22228
