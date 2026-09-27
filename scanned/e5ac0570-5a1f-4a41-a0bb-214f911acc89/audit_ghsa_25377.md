# [H] Exposure of Resource to Wrong Sphere in Spring Cloud OpenFeign

## Summary
Severity: High
Advisory: GHSA-pf94-6v2v-cm3j
CVE: CVE-2021-22044
CWE: CWE-668
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-pf94-6v2v-cm3j
Type: github-advisory

## Affected
- Maven: `org.springframework.cloud:spring-cloud-openfeign-core` — affected >=3.0.0 <3.0.5
- Maven: `org.springframework.cloud:spring-cloud-openfeign-core` — affected >=2.2.0 <2.2.10

## Details
In Spring Cloud OpenFeign 3.0.0 to 3.0.4, 2.2.0.RELEASE to 2.2.9.RELEASE, and older unsupported versions, applications using type-level `@RequestMapping`annotations over Feign client interfaces, can be involuntarily exposing endpoints corresponding to `@RequestMapping`-annotated interface methods.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-22044
- https://tanzu.vmware.com/security/cve-2021-22044
