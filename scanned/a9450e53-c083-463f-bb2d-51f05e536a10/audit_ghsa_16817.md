# [H] Spring Framework URL Parsing with Host Validation

## Summary
Severity: High
Advisory: GHSA-2wrp-6fg6-hmc5
CVE: CVE-2024-22262
CWE: CWE-601
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-04-16
Source: https://github.com/advisories/GHSA-2wrp-6fg6-hmc5
Type: github-advisory

## Affected
- Maven: `org.springframework:spring-web` — affected >=0 <5.3.34
- Maven: `org.springframework:spring-web` — affected >=6.0.0 <6.0.19
- Maven: `org.springframework:spring-web` — affected >=6.1.0 <6.1.6

## Details
Applications that use UriComponentsBuilder to parse an externally provided URL (e.g. through a query parameter) AND perform validation checks on the host of the parsed URL may be vulnerable to a  open redirect https://cwe.mitre.org/data/definitions/601.html  attack or to a SSRF attack if the URL is used after passing validation checks.

This is the same as  CVE-2024-22259 https://spring.io/security/cve-2024-22259  and  CVE-2024-22243 https://spring.io/security/cve-2024-22243 , but with different input.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-22262
- https://github.com/spring-projects/spring-framework
- https://github.com/spring-projects/spring-framework/blob/main/spring-web/src/main/java/org/springframework/web/util/UriComponentsBuilder.java
- https://security.netapp.com/advisory/ntap-20240524-0003
- https://spring.io/security/cve-2024-22262
