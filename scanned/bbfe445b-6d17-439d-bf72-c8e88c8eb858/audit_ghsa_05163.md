# [M] Spring Framework Cross-site Scripting via JSP Form Tags

## Summary
Severity: Medium
Advisory: GHSA-957g-f97v-vppc
CVE: CVE-2026-41846
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-06-09
Source: https://github.com/advisories/GHSA-957g-f97v-vppc
Type: github-advisory

## Affected
- Maven: `org.springframework:spring-webmvc` — affected >=7.0.0 <7.0.8
- Maven: `org.springframework:spring-webmvc` — affected >=6.2.0 <6.2.19
- Maven: `org.springframework:spring-webmvc` — affected >=6.1.0
- Maven: `org.springframework:spring-webmvc` — affected >=0

## Details
Spring MVC applications which accept user-supplied values in the cssClass, cssErrorClass, or cssStyle attributes of JSP form tags allow arbitrary HTML/JavaScript code injection, potentially resulting in a cross-site scripting (XSS) vulnerability.

Affected versions:
Spring Framework 7.0.0 through 7.0.7; 6.2.0 through 6.2.18; 6.1.0 through 6.1.27; 5.3.0 through 5.3.48.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-41846
- https://github.com/spring-projects/spring-framework/commit/1829b42b9c45e780c268dd17863d9198d62154d3
- https://github.com/spring-projects/spring-framework/commit/e8f10244e3859e8bb5b6be3823c9bbea2c130573
- https://github.com/spring-projects/spring-framework
- https://github.com/spring-projects/spring-framework/releases/tag/v6.2.19
- https://github.com/spring-projects/spring-framework/releases/tag/v7.0.8
- https://spring.io/security/cve-2026-41846
