# [M] Spring Framework Server-Side Request Forgery via UriComponentsBuilder

## Summary
Severity: Medium
Advisory: GHSA-7m2p-62gw-p8qq
CVE: CVE-2026-41854
CWE: CWE-918
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-09
Source: https://github.com/advisories/GHSA-7m2p-62gw-p8qq
Type: github-advisory

## Affected
- Maven: `org.springframework:spring-web` — affected >=7.0.0 <7.0.8
- Maven: `org.springframework:spring-web` — affected >=6.2.0 <6.2.19

## Details
Due to incorrect host parsing, applications that rely on UriComponentsBuilder to parse and validate an externally provided URL string may be exposed to a server-side request forgery (SSRF) attack.

Affected versions:
Spring Framework 7.0.0 through 7.0.7; 6.2.0 through 6.2.18.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-41854
- https://github.com/spring-projects/spring-framework
- https://spring.io/security/cve-2026-41854
