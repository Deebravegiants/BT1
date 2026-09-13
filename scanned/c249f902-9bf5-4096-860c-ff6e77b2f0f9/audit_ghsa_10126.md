# [M] Spring Security Core has a TOCTOU race condition when One-Time Token login with JdbcOneTimeTokenService is configured

## Summary
Severity: Medium
Advisory: GHSA-x2wq-9x2f-fhj7
CVE: CVE-2026-22751
CWE: CWE-367
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-21
Source: https://github.com/advisories/GHSA-x2wq-9x2f-fhj7
Type: github-advisory

## Affected
- Maven: `org.springframework.security:spring-security-core` — affected >=6.5.0 <6.5.10
- Maven: `org.springframework.security:spring-security-core` — affected >=7.0.3 <7.0.5
- Maven: `org.springframework.security:spring-security-core` — affected >=6.4.0

## Details
Vulnerability in Spring Spring Security. Applications that explicitly configure One-Time Token login with JdbcOneTimeTokenService are vulnerable to a Time-of-check Time-of-use (TOCTOU) race condition. This issue affects Spring Security: from 6.4.0 through 6.4.15, from 6.5.0 through 6.5.9, from 7.0.0 through 7.0.4.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-22751
- https://github.com/spring-projects/spring-security/commit/163772775036c4146815a5266874278c6f45f047
- https://github.com/spring-projects/spring-security/commit/4187af38b251fc97fdf9949f7869618111e6e261
- https://github.com/spring-projects/spring-security
- https://jinyeong.seol.pro/blogs/cve-2026-22751/en
- https://spring.io/security/cve-2026-22751
