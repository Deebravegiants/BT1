# [M] Exposure of Sensitive Information to an Unauthorized Actor and SQL Injection in Spring Data JPA

## Summary
Severity: Medium
Advisory: GHSA-jgmr-wrwx-mgfj
CVE: CVE-2019-3797
CWE: CWE-200, CWE-89
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2019-05-14
Source: https://github.com/advisories/GHSA-jgmr-wrwx-mgfj
Type: github-advisory

## Affected
- Maven: `org.springframework.data:spring-data-jpa` — affected >=0 <1.11.20
- Maven: `org.springframework.data:spring-data-jpa` — affected >=2.0.0 <2.0.14
- Maven: `org.springframework.data:spring-data-jpa` — affected >=2.1.0 <2.1.6

## Details
This affects Spring Data JPA in versions up to and including 2.1.5, 2.0.13 and 1.11.19. Derived queries using any of the predicates ?startingWith?, ?endingWith? or ?containing? could return more results than anticipated when a maliciously crafted query parameter value is supplied. Also, LIKE expressions in manually defined queries could return unexpected results if the parameter values bound did not have escaped reserved characters properly.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-3797
- https://pivotal.io/security/cve-2019-3797
