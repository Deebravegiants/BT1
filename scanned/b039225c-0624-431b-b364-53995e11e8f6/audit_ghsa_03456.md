# [M] Externally Controlled Reference to a Resource in Another Sphere and Confused Deputy in Spring Cloud Netflix

## Summary
Severity: Medium
Advisory: GHSA-qgcg-p3v2-9h4p
CVE: CVE-2020-5412
CWE: CWE-441, CWE-610
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:L/I:H/A:N (CVSS_V3)
Published: 2021-04-30
Source: https://github.com/advisories/GHSA-qgcg-p3v2-9h4p
Type: github-advisory

## Affected
- Maven: `org.springframework.cloud:spring-cloud-netflix` — affected >=2.2.0 <2.2.4
- Maven: `org.springframework.cloud:spring-cloud-netflix` — affected >=2.1.0 <2.1.6

## Details
Spring Cloud Netflix, versions 2.2.x prior to 2.2.4, versions 2.1.x prior to 2.1.6, and older unsupported versions allow applications to use the Hystrix Dashboard proxy.stream endpoint to make requests to any server reachable by the server hosting the dashboard. A malicious user, or attacker, can send a request to other servers that should not be exposed publicly.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-5412
- https://tanzu.vmware.com/security/cve-2020-5412
