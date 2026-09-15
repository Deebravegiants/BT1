# [M] Spring Security Vulnerable to Unauthorized User Impersonation when Using X.509 Client Certificates

## Summary
Severity: Medium
Advisory: GHSA-293q-567p-wmwq
CVE: CVE-2026-47838
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-10
Source: https://github.com/advisories/GHSA-293q-567p-wmwq
Type: github-advisory

## Affected
- Maven: `org.springframework.security:spring-security-web` — affected >=6.5.0 <6.5.11
- Maven: `org.springframework.security:spring-security-web` — affected >=6.4.0
- Maven: `org.springframework.security:spring-security-web` — affected >=6.0.0
- Maven: `org.springframework.security:spring-security-web` — affected >=5.8.0
- Maven: `org.springframework.security:spring-security-web` — affected >=0

## Details
In Spring Security Web, `SubjectDnX509PrincipalExtractor` does not correctly handle certain malformed X.509 certificate CN values, which can lead to reading the wrong value for the username. In a carefully crafted certificate, this can lead to an attacker impersonating another user.

`SubjectDnX509PrincipalExtractor` is deprecated by this CVE and replaced with `SubjectX500PrincipalExtractor`. As part of updating, you should also migrate to `SubjectX500PrincipalExtractor`.

Affected versions:
Spring Security Enterprise 5.7.0 through 5.7.24; 5.8.0 through 5.8.26; 6.3.0 through 6.3.17; 6.4.0 through 6.4.17; 6.5.0 through 6.5.10. 
OSS 6.5.0 through 6.5.10.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-47838
- https://github.com/advisories/GHSA-2jrg-rf5x-568g
- https://spring.io/security/cve-2026-47838
- spring-projects/spring-security
