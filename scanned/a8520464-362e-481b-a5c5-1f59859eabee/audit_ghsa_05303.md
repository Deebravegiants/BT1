# [M] Spring Web Flow has Data Binding Vulnerability with Unified EL Parser

## Summary
Severity: Medium
Advisory: GHSA-9ggw-87m9-9gfc
CVE: CVE-2026-40985
CWE: CWE-917
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-11
Source: https://github.com/advisories/GHSA-9ggw-87m9-9gfc
Type: github-advisory

## Affected
- Maven: `org.springframework.webflow:spring-webflow` — affected >=4.0.0 <4.0.1
- Maven: `org.springframework.webflow:spring-webflow` — affected >=3.0.0 <3.0.2
- Maven: `org.springframework.webflow:spring-webflow` — affected >=0

## Details
Applications that configure the WebFlowELExpressionParser are vulnerable to the use of malicious Unified EL expressions.

Affected versions:
Spring Web Flow 4.0.0; 3.0.0 through 3.0.1; 2.5.0 through 2.5.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-40985
- https://github.com/spring-projects/spring-webflow
- https://spring.io/security/cve-2026-40985
