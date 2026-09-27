# [M] Spring REST Docs REST Assured & WebFlux are vulnerable to Improper Restriction of XML External Entity Reference

## Summary
Severity: Medium
Advisory: GHSA-6rpq-6vv2-5222
CVE: CVE-2026-40991
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:N/A:L (CVSS_V3)
Published: 2026-06-10
Source: https://github.com/advisories/GHSA-6rpq-6vv2-5222
Type: github-advisory

## Affected
- Maven: `org.springframework.restdocs:spring-restdocs-webtestclient` — affected >=4.0.0 <4.0.1
- Maven: `org.springframework.restdocs:spring-restdocs-webtestclient` — affected >=3.0.0 <3.0.6
- Maven: `org.springframework.restdocs:spring-restdocs-webtestclient` — affected >=0
- Maven: `org.springframework.restdocs:spring-restdocs-restassured` — affected >=4.0.0 <4.0.1
- Maven: `org.springframework.restdocs:spring-restdocs-restassured` — affected >=3.0.0 <3.0.6
- Maven: `org.springframework.restdocs:spring-restdocs-restassured` — affected >=0

## Details
When using spring-restdocs-webtestclient or spring-restdocs-restassured to document a remote API accessed over HTTP, an attacker who compromises the API or tricks the user into documenting a malicious API can perform an XXE injection attack when the documentation-generating tests are next executed.

Affected versions:
Spring REST Docs 4.0.0; 3.0.0 through 3.0.5; 2.0.0.RELEASE through 2.0.8.RELEASE.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-40991
- https://github.com/spring-projects/spring-restdocs
- https://github.com/spring-projects/spring-restdocs/releases/tag/v3.0.6
- https://github.com/spring-projects/spring-restdocs/releases/tag/v4.0.1
- https://spring.io/security/cve-2026-40991
