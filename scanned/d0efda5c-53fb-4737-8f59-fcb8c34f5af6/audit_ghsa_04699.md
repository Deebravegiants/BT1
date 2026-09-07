# [M] Spring Framework Security Filter Bypass in WebFlux Kotlin Router DSL

## Summary
Severity: Medium
Advisory: GHSA-vqgp-pf68-6947
CVE: CVE-2026-41847
CWE: CWE-284
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-09
Source: https://github.com/advisories/GHSA-vqgp-pf68-6947
Type: github-advisory

## Affected
- Maven: `org.springframework:spring-webflux` — affected >=0

## Details
Spring WebFlux applications may be vulnerable to a security bypass when using the Kotlin Router DSL.

Affected versions:
Spring Framework 5.3.0 through 5.3.48.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-41847
- https://github.com/spring-projects/spring-framework
- https://spring.io/security/cve-2026-41847
