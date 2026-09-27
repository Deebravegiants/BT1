# [M] Directory traversal attack in Spring Cloud Config

## Summary
Severity: Medium
Advisory: GHSA-g86w-v5vg-9gxf
CVE: CVE-2020-5405
CWE: CWE-22, CWE-23
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2020-06-05
Source: https://github.com/advisories/GHSA-g86w-v5vg-9gxf
Type: github-advisory

## Affected
- Maven: `org.springframework.cloud:spring-cloud-config-server` — affected >=2.1.0 <2.1.7
- Maven: `org.springframework.cloud:spring-cloud-config-server` — affected >=2.2.0 <2.2.2

## Details
Spring Cloud Config, versions 2.2.x prior to 2.2.2, versions 2.1.x prior to 2.1.7, and older unsupported versions allow applications to serve arbitrary configuration files through the spring-cloud-config-server module. A malicious user, or attacker, can send a request using a specially crafted URL that can lead a directory traversal attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-5405
- https://github.com/spring-cloud/spring-cloud-config/spring-cloud-config-server
- https://pivotal.io/security/cve-2020-5405
