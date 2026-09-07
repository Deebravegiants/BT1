# [M] Spring Security OAuth2 Authorization Server: Authorization endpoint performs insufficient validation of the request_uri parameter

## Summary
Severity: Medium
Advisory: GHSA-4r8w-73jc-3m7q
CVE: CVE-2026-41008
CWE: CWE-601
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-10
Source: https://github.com/advisories/GHSA-4r8w-73jc-3m7q
Type: github-advisory

## Affected
- Maven: `org.springframework.security:spring-security-oauth2-authorization-server` — affected >=7.0.0 <7.0.6
- Maven: `org.springframework.security:spring-security-oauth2-authorization-server` — affected >=1.5.0 <1.5.8

## Details
Spring Security Authorization Server's authorization endpoint performs insufficient validation of the request_uri parameter. An attacker can craft a malicious authorization request containing an invalid request_uri and an arbitrary, unvalidated redirect_uri, which can lead to an Open Redirect vulnerability.

Affected versions:
Spring Security 7.0.0 through 7.0.5.
Spring Authorization Server 1.5.0 through 1.5.7.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-41008
- https://github.com/spring-projects/spring-authorization-server
- https://github.com/spring-projects/spring-security/releases/tag/7.0.6
- https://spring.io/security/cve-2026-41008
