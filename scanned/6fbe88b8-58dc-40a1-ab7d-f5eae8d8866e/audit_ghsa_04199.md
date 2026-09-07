# [H] Spring Framework Cross-site Scripting via JavaScriptUtils

## Summary
Severity: High
Advisory: GHSA-3chg-m5w7-qfv5
CVE: CVE-2026-41845
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-06-09
Source: https://github.com/advisories/GHSA-3chg-m5w7-qfv5
Type: github-advisory

## Affected
- Maven: `org.springframework:spring-webmvc` — affected >=7.0.0 <7.0.8
- Maven: `org.springframework:spring-webmvc` — affected >=6.2.0 <6.2.19
- Maven: `org.springframework:spring-webmvc` — affected >=6.1.0
- Maven: `org.springframework:spring-webmvc` — affected >=0

## Details
Due to incorrect escaping, the use of JavaScriptUtils.javaScriptEscape() may lead to JavaScript code injection in the browser, potentially resulting in a cross-site scripting (XSS) vulnerability.

Affected versions:
Spring Framework 7.0.0 through 7.0.7; 6.2.0 through 6.2.18; 6.1.0 through 6.1.27; 5.3.0 through 5.3.48.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-41845
- https://github.com/spring-projects/spring-framework/commit/86d99790dbaa8ce6bb1087ef92844d0abfdab015
- https://github.com/spring-projects/spring-framework/commit/a1826b725c29fbb175fa7b4fc005aa3d78c32015
- https://github.com/spring-projects/spring-framework
- https://github.com/spring-projects/spring-framework/releases/tag/v6.2.19
- https://github.com/spring-projects/spring-framework/releases/tag/v7.0.8
- https://spring.io/security/cve-2026-41845
