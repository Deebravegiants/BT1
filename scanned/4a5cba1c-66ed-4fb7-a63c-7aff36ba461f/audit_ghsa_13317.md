# [M] Spring HATEOAS vulnerable to Improper Neutralization of HTTP Headers for Scripting Syntax

## Summary
Severity: Medium
Advisory: GHSA-7m5c-fgwf-mwph
CVE: CVE-2023-34036
CWE: CWE-116, CWE-644
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-07-17
Source: https://github.com/advisories/GHSA-7m5c-fgwf-mwph
Type: github-advisory

## Affected
- Maven: `org.springframework.hateoas:spring-hateoas` — affected >=0 <1.5.5
- Maven: `org.springframework.hateoas:spring-hateoas` — affected >=2.0.0 <2.0.5
- Maven: `org.springframework.hateoas:spring-hateoas` — affected >=2.1.0 <2.1.1

## Details
Reactive web applications that use Spring HATEOAS to produce hypermedia-based responses might be exposed to malicious forwarded headers if they are not behind a trusted proxy that ensures correctness of such headers, or if they don't have anything else in place to handle (and possibly discard) forwarded headers either in WebFlux or at the level of the underlying HTTP server.

For the application to be affected, it needs to satisfy the following requirements:

  *  It needs to use the reactive web stack (Spring WebFlux) and Spring HATEOAS to create links in hypermedia-based responses.
  *  The application infrastructure does not guard against clients submitting (X-)Forwarded… headers.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-34036
- https://github.com/spring-projects/spring-hateoas
- https://spring.io/security/cve-2023-34036
