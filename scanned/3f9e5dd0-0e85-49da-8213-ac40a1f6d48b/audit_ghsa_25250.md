# [H] Improper Restriction of XML External Entity Reference in Spring Framework

## Summary
Severity: High
Advisory: GHSA-f93f-g33r-8pcp
CVE: CVE-2014-0225
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-f93f-g33r-8pcp
Type: github-advisory

## Affected
- Maven: `org.springframework:spring-webmvc` — affected >=4.0.0 <4.0.5
- Maven: `org.springframework:spring-webmvc` — affected >=3.0.0 <3.2.8

## Details
When processing user provided XML documents, the Spring Framework 4.0.0 to 4.0.4, 3.0.0 to 3.2.8, and possibly earlier unsupported versions did not disable by default the resolution of URI references in a DTD declaration. This enabled an XXE attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-0225
- https://github.com/spring-projects/spring-framework/commit/44ee51a6c9c3734b3fcf9a20817117e86047d753
- https://github.com/spring-projects/spring-framework/commit/8e096aeef55287dc829484996c9330cf755891a1
- https://github.com/spring-projects/spring-framework/commit/c6503ebbf7c9e21ff022c58706dbac5417b2b5eb
- https://jira.spring.io/browse/SPR-11768
- https://pivotal.io/security/cve-2014-0225
