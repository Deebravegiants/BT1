# [H] Spring Web Services: Jaxp13 XPath XXE via StreamSource and SAXSource

## Summary
Severity: High
Advisory: GHSA-2mpf-m756-hxjm
CVE: CVE-2026-40998
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-06-11
Source: https://github.com/advisories/GHSA-2mpf-m756-hxjm
Type: github-advisory

## Affected
- Maven: `org.springframework.ws:spring-xml` — affected >=5.0.0 <5.0.2
- Maven: `org.springframework.ws:spring-xml` — affected >=4.1.0 <4.1.4
- Maven: `org.springframework.ws:spring-xml` — affected >=4.0.0
- Maven: `org.springframework.ws:spring-xml` — affected >=3.1.0

## Details
Jaxp13XPathTemplate evaluated XPath expressions for StreamSource and SAXSource inputs using a code path that parsed attacker-controlled XML with the JDK's default DocumentBuilderFactory behavior instead of Spring's hardened parser configuration. Applications that evaluate XPath against untrusted XML payloads could therefore be exposed to XML External Entity (XXE) style attacks.

Affected versions:
Spring Web Services 5.0.0 through 5.0.1; 4.1.0 through 4.1.3; 4.0.0 through 4.0.18; 3.1.0 through 3.1.8.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-40998
- https://github.com/spring-projects/spring-ws/commit/eb8d66c0995d1e1dd5bfcfb657c8c9de21266d97
- https://github.com/spring-projects/spring-ws
- https://spring.io/security/cve-2026-40998
