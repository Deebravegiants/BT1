# [M] Spring Framework DoS with Multipart Temp Files in WebFlux

## Summary
Severity: Medium
Advisory: GHSA-5843-p793-ghmm
CVE: CVE-2026-22740
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-29
Source: https://github.com/advisories/GHSA-5843-p793-ghmm
Type: github-advisory

## Affected
- Maven: `org.springframework:spring-webflux` — affected >=7.0.0 <7.0.7
- Maven: `org.springframework:spring-webflux` — affected >=6.2.0 <6.2.18
- Maven: `org.springframework:spring-webflux` — affected >=6.1.0
- Maven: `org.springframework:spring-webflux` — affected >=0

## Details
A WebFlux server application that processes multipart requests creates temp files for parts larger than 10 K. Under some circumstances, temp files may remain not deleted after the request is fully processed. This allows an attacker to consume available disk space.

Older, unsupported versions are also affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-22740
- https://github.com/spring-projects/spring-framework
- https://spring.io/security/cve-2026-22740
