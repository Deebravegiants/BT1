# [H] Spring Security Doesn't Correctly Include Servlet Path in Path Matching of HttpSecurity#securityMatchers

## Summary
Severity: High
Advisory: GHSA-4wrg-8wpc-h923
CVE: CVE-2026-22753
CWE: CWE-693
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-4wrg-8wpc-h923
Type: github-advisory

## Affected
- Maven: `org.springframework.security:spring-security-config` — affected >=7.0.0 <7.0.5

## Details
Vulnerability in Spring Spring Security. If an application is using securityMatchers(String) and a PathPatternRequestMatcher.Builder bean to prepend a servlet path, matching requests to that filter chain may fail and its related security components will not be exercised as intended by the application. This can lead to the authentication, authorization, and other security controls being rendered inactive on intended requests. This issue affects Spring Security: from 7.0.0 through 7.0.4.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-22753
- https://github.com/spring-projects/spring-security
- https://spring.io/security/cve-2026-22753
