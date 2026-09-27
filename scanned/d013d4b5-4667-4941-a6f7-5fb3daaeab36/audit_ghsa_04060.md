# [M] Path Traversal in Spring Cloud Config

## Summary
Severity: Medium
Advisory: GHSA-4x49-w62v-76q7
CVE: CVE-2019-3799
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2019-05-23
Source: https://github.com/advisories/GHSA-4x49-w62v-76q7
Type: github-advisory

## Affected
- Maven: `org.springframework.cloud:spring-cloud-config-server` — affected >=0 <1.4.6
- Maven: `org.springframework.cloud:spring-cloud-config-server` — affected >=2.0.0 <2.0.4
- Maven: `org.springframework.cloud:spring-cloud-config-server` — affected >=2.1.0 <2.1.2

## Details
Spring Cloud Config, versions 2.1.x prior to 2.1.2, versions 2.0.x prior to 2.0.4, and versions 1.4.x prior to 1.4.6, and older unsupported versions allow applications to serve arbitrary configuration files through the spring-cloud-config-server module. A malicious user, or attacker, can send a request using a specially crafted URL that can lead a directory traversal attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-3799
- https://github.com/mpgn/CVE-2019-3799
- https://pivotal.io/security/cve-2019-3799
- https://www.oracle.com/security-alerts/cpuapr2022.html
