# [M] Improper Neutralization of Wildcards or Matching Symbols

## Summary
Severity: Medium
Advisory: GHSA-xggx-fx6w-v7ch
CVE: CVE-2019-3802
CWE: CWE-155, CWE-200
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2019-06-04
Source: https://github.com/advisories/GHSA-xggx-fx6w-v7ch
Type: github-advisory

## Affected
- Maven: `org.springframework.data:spring-data-jpa` — affected >=2.1.0 <2.1.8
- Maven: `org.springframework.data:spring-data-jpa` — affected >=2.0.0 <2.1.8
- Maven: `org.springframework.data:spring-data-jpa` — affected >=0 <1.11.22

## Details
This affects Spring Data JPA in versions up to and including 2.1.6, 2.0.14 and 1.11.20. ExampleMatcher using ExampleMatcher.StringMatcher.STARTING, ExampleMatcher.StringMatcher.ENDING or ExampleMatcher.StringMatcher.CONTAINING could return more results than anticipated when a maliciously crafted example value is supplied.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-3802
- https://pivotal.io/security/cve-2019-3802
