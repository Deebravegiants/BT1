# [H] Spring Framework Path Traversal vulnerability

## Summary
Severity: High
Advisory: GHSA-g5vr-rgqm-vf78
CVE: CVE-2024-38819
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-12-19
Source: https://github.com/advisories/GHSA-g5vr-rgqm-vf78
Type: github-advisory

## Affected
- Maven: `org.springframework:spring-webflux` — affected >=6.1.0 <6.1.14
- Maven: `org.springframework:spring-webmvc` — affected >=6.1.0 <6.1.14
- Maven: `org.springframework:spring-webflux` — affected >=0
- Maven: `org.springframework:spring-webmvc` — affected >=0
- Maven: `org.springframework:spring-webflux` — affected >=6.0.0
- Maven: `org.springframework:spring-webmvc` — affected >=6.0.0

## Details
Applications serving static resources through the functional web frameworks WebMvc.fn or WebFlux.fn are vulnerable to path traversal attacks. An attacker can craft malicious HTTP requests and obtain any file on the file system that is also accessible to the process in which the Spring application is running.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-38819
- https://github.com/spring-projects/spring-framework/issues/33689
- https://github.com/spring-projects/spring-framework/commit/3bfbe30a7814c9ea1556d40df9bd87ddb3ba372d
- https://github.com/spring-projects/spring-framework/commit/fb7890d73975a3d9e0763e0926df2bd0a608e87e
- https://github.com/spring-projects/spring-framework
- https://security.netapp.com/advisory/ntap-20250110-0010
- https://spring.io/security/cve-2024-38819
