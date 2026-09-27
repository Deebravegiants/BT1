# [M] Spring Security has a broken timing attack mitigation implemented in DaoAuthenticationProvide

## Summary
Severity: Medium
Advisory: GHSA-vqxh-445g-37fc
CVE: CVE-2025-22234
CWE: CWE-208
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-01-22
Source: https://github.com/advisories/GHSA-vqxh-445g-37fc
Type: github-advisory

## Affected
- Maven: `org.springframework.security:spring-security-core` — affected >=6.3.8 <6.3.9
- Maven: `org.springframework.security:spring-security-core` — affected >=6.4.4 <6.4.5

## Details
The fix applied in CVE-2025-22228 inadvertently broke the timing attack mitigation implemented in DaoAuthenticationProvider. This can allow attackers to infer valid usernames or other authentication behavior via response-time differences under certain configurations.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-22234
- https://github.com/spring-projects/spring-security
- https://spring.io/security/cve-2025-22234
