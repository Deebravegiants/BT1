# [M] Spring Framework Improper Path Limitation with Script View Templates

## Summary
Severity: Medium
Advisory: GHSA-4773-3jfm-qmx3
CVE: CVE-2026-22737
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-20
Source: https://github.com/advisories/GHSA-4773-3jfm-qmx3
Type: github-advisory

## Affected
- Maven: `org.springframework:spring-webmvc` — affected >=7.0.0-M1 <7.0.6
- Maven: `org.springframework:spring-webmvc` — affected >=6.2.0 <6.2.17
- Maven: `org.springframework:spring-webmvc` — affected >=6.0.0
- Maven: `org.springframework:spring-webmvc` — affected >=5.3.0
- Maven: `org.springframework:spring-webflux` — affected >=7.0.0-M1 <7.0.6
- Maven: `org.springframework:spring-webflux` — affected >=6.2.0 <6.2.17
- Maven: `org.springframework:spring-webflux` — affected >=6.0.0
- Maven: `org.springframework:spring-webflux` — affected >=5.3.0

## Details
Use of Java scripting engine enabled (e.g. JRuby, Jython) template views in Spring MVC and Spring WebFlux applications can result in disclosure of content from files outside the configured locations for script template views. This issue affects Spring Framework: from 7.0.0 through 7.0.5, from 6.2.0 through 6.2.16, from 6.1.0 through 6.1.25, from 5.3.0 through 5.3.46.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-22737
- https://github.com/spring-projects/spring-framework
- https://spring.io/security/cve-2026-22737
