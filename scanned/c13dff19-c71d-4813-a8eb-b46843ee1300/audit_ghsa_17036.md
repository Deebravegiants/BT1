# [M] Improper Authentication in Spring Authorization Server

## Summary
Severity: Medium
Advisory: GHSA-x637-x8p3-5p22
CVE: CVE-2024-22258
CWE: CWE-287, CWE-470
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-03-20
Source: https://github.com/advisories/GHSA-x637-x8p3-5p22
Type: github-advisory

## Affected
- Maven: `org.springframework.security:spring-security-oauth2-authorization-server` — affected >=0 <1.1.6
- Maven: `org.springframework.security:spring-security-oauth2-authorization-server` — affected >=1.2.0 <1.2.3

## Details
Spring Authorization Server versions 1.0.0 - 1.0.5, 1.1.0 - 1.1.5, 1.2.0 - 1.2.2 and older unsupported versions are susceptible to a PKCE Downgrade Attack for Confidential Clients.

Specifically, an application is vulnerable when a Confidential Client uses PKCE for the Authorization Code Grant.

An application is not vulnerable when a Public Client uses PKCE for the Authorization Code Grant.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-22258
- https://github.com/spring-projects/spring-authorization-server/commit/a7035d22bd2de6c24e7125623d38fb83d8f659a9
- https://spring.io/security/cve-2024-22258
- github.com/spring-projects/spring-authorization-server
