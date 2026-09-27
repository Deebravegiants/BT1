# [M] Spring LDAP data exposure vulnerability

## Summary
Severity: Medium
Advisory: GHSA-mqvr-2rp8-j7h4
CVE: CVE-2024-38829
CWE: CWE-178
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-12-04
Source: https://github.com/advisories/GHSA-mqvr-2rp8-j7h4
Type: github-advisory

## Affected
- Maven: `org.springframework.ldap:spring-ldap-core` — affected >=3.0.0 <3.2.8
- Maven: `org.springframework.ldap:spring-ldap-core` — affected >=0 <2.4.4

## Details
A vulnerability in Spring LDAP allows data exposure for case sensitive comparisons.This issue affects Spring LDAP: from 2.4.0 through 2.4.3, from 3.0.0 through 3.0.9, from 3.1.0 through 3.1.7, from 3.2.0 through 3.2.7, AND all versions prior to 2.4.0.

The usage of String.toLowerCase() and String.toUpperCase() has some Locale dependent exceptions that could potentially result in unintended columns from being queried
Related to CVE-2024-38820 https://spring.io/security/cve-2024-38820

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-38829
- https://github.com/spring-projects/spring-ldap
- https://spring.io/security/cve-2024-38829
