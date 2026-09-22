# [M] Spring Security Missing Authorization vulnerability

## Summary
Severity: Medium
Advisory: GHSA-hmqf-wpq9-jq83
CVE: CVE-2024-38810
CWE: CWE-287, CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-08-20
Source: https://github.com/advisories/GHSA-hmqf-wpq9-jq83
Type: github-advisory

## Affected
- Maven: `org.springframework.security:spring-security-core` — affected >=6.3.0 <6.3.2

## Details
Missing Authorization When Using @AuthorizeReturnObject in Spring Security 6.3.0 and 6.3.1 allows attacker to render security annotations inaffective.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-38810
- https://github.com/spring-projects/spring-security
- https://spring.io/security/cve-2024-38810
