# [H] Spring Security Doesn't Correctly Include Servlet Path in Path Matching of XML Authorization Rules

## Summary
Severity: High
Advisory: GHSA-4vrc-j85c-598c
CVE: CVE-2026-22754
CWE: CWE-284
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-4vrc-j85c-598c
Type: github-advisory

## Affected
- Maven: `org.springframework.security:spring-security-config` — affected >=7.0.0 <7.0.5

## Details
Vulnerability in Spring Spring Security. If an application uses <sec:intercept-url servlet-path="/servlet-path" pattern="/endpoint/**"/> to define the servlet path for computing a path matcher, then the servlet path is not included and the related authorization rules are not exercised. This can lead to an authorization bypass. This issue affects Spring Security: from 7.0.0 through 7.0.4.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-22754
- https://github.com/spring-projects/spring-security
- https://spring.io/security/cve-2026-22754
