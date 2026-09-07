# [M] Spring Security: Open Redirect via Unvalidated Post-Login Redirect URL Stored in CookieRequestCache

## Summary
Severity: Medium
Advisory: GHSA-x2r2-rvhq-2mqv
CVE: CVE-2026-41706
CWE: CWE-601
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-10
Source: https://github.com/advisories/GHSA-x2r2-rvhq-2mqv
Type: github-advisory

## Affected
- Maven: `org.springframework.security:spring-security-web` — affected >=7.0.0 <7.0.6
- Maven: `org.springframework.security:spring-security-web` — affected >=6.5.0 <6.5.11
- Maven: `org.springframework.security:spring-security-web` — affected >=6.3.0
- Maven: `org.springframework.security:spring-security-web` — affected >=5.8.0
- Maven: `org.springframework.security:spring-security-web` — affected >=0

## Details
Spring Security's CookieRequestCache and CookieServerRequestCache store the pre-authentication request URL in a browser cookie so that users can be redirected back to their intended destination after a successful login. In affected versions, the full absolute URL is stored in the cookie and is used without validation as the post-login redirect target.

Affected versions:
Spring Security 5.7.0 through 5.7.23; 5.8.0 through 5.8.25; 6.3.0 through 6.3.16; 6.4.0 through 6.4.16; 6.5.0 through 6.5.10; 7.0.0 through 7.0.5.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-41706
- https://github.com/spring-projects/spring-security
- https://github.com/spring-projects/spring-security/releases/tag/6.5.11
- https://github.com/spring-projects/spring-security/releases/tag/7.0.6
- https://spring.io/security/cve-2026-41706
