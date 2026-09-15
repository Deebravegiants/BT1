# [M] Exposure of Resource to Wrong Sphere in Spring Data REST

## Summary
Severity: Medium
Advisory: GHSA-4926-qpxg-6r3w
CVE: CVE-2021-22047
CWE: CWE-668
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-4926-qpxg-6r3w
Type: github-advisory

## Affected
- Maven: `org.springframework.data:spring-data-rest-core` — affected >=3.4.0 <3.4.14
- Maven: `org.springframework.data:spring-data-rest-core` — affected >=3.5.0 <3.5.6

## Details
In Spring Data REST versions 3.4.0 - 3.4.13, 3.5.0 - 3.5.5, and older unsupported versions, HTTP resources implemented by custom controllers using a configured base API path and a controller type-level request mapping are additionally exposed under URIs that can potentially be exposed for unauthorized access depending on the Spring Security configuration.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-22047
- https://tanzu.vmware.com/security/cve-2021-22047
