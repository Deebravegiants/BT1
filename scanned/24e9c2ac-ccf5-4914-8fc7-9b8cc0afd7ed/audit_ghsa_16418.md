# [H] Spring Web vulnerable to Open Redirect or Server Side Request Forgery

## Summary
Severity: High
Advisory: GHSA-ccgv-vj62-xf9h
CVE: CVE-2024-22243
CWE: CWE-601
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-02-23
Source: https://github.com/advisories/GHSA-ccgv-vj62-xf9h
Type: github-advisory

## Affected
- Maven: `org.springframework:spring-web` — affected >=6.1.0 <6.1.4
- Maven: `org.springframework:spring-web` — affected >=6.0.0 <6.0.17
- Maven: `org.springframework:spring-web` — affected >=5.3.0 <5.3.32
- Maven: `org.springframework:spring-web` — affected >=0

## Details
Applications that use UriComponentsBuilder to parse an externally provided URL (e.g. through a query parameter) AND perform validation checks on the host of the parsed URL may be vulnerable to a  open redirect attack or to a SSRF attack if the URL is used after passing validation checks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-22243
- https://github.com/spring-projects/spring-framework
- https://github.com/spring-projects/spring-framework/blob/main/spring-web/src/main/java/org/springframework/web/util/UriComponentsBuilder.java
- https://security.netapp.com/advisory/ntap-20240524-0001
- https://spring.io/security/cve-2024-22243
- http://seclists.org/fulldisclosure/2024/Sep/24
