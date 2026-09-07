# [H] SQL Injection in Spring AI MariaDBFilterExpressionConverter

## Summary
Severity: High
Advisory: GHSA-c267-rfvc-mvpm
CVE: CVE-2026-22730
CWE: CWE-89
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-c267-rfvc-mvpm
Type: github-advisory

## Affected
- Maven: `org.springframework.ai:spring-ai-mariadb-store` — affected >=1.1.0-M1 <1.1.3
- Maven: `org.springframework.ai:spring-ai-mariadb-store` — affected >=0 <1.0.4

## Details
A critical SQL injection vulnerability in Spring AI's MariaDBFilterExpressionConverter allows attackers to bypass metadata-based access controls and execute arbitrary SQL commands.

The vulnerability exists due to missing input sanitization.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-22730
- https://github.com/spring-projects/spring-ai
- https://github.com/spring-projects/spring-ai/releases/tag/v1.0.4
- https://github.com/spring-projects/spring-ai/releases/tag/v1.1.3
- https://spring.io/security/cve-2026-22730
