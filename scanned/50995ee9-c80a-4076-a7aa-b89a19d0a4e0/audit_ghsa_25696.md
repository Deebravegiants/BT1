# [M] Denial of service in Spring Security OAuth2

## Summary
Severity: Medium
Advisory: GHSA-c2cp-3xj9-97w9
CVE: CVE-2022-22969
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-04-22
Source: https://github.com/advisories/GHSA-c2cp-3xj9-97w9
Type: github-advisory

## Affected
- Maven: `org.springframework.security.oauth:spring-security-oauth2` — affected >=2.5.0.RELEASE <2.5.2.RELEASE
- Maven: `org.springframework.security.oauth:spring-security-oauth2` — affected >=2.4.0.RELEASE <2.4.2.RELEASE

## Details
Spring Security OAuth versions 2.5.x prior to 2.5.2 and older unsupported versions are susceptible to a Denial-of-Service (DoS) attack via the initiation of the Authorization Request in an OAuth 2.0 Client application. A malicious user or attacker can send multiple requests initiating the Authorization Request for the Authorization Code Grant, which has the potential of exhausting system resources using a single session. This vulnerability exposes OAuth 2.0 Client applications only.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-22969
- https://spring.io/security/cve-2022-22969
- https://tanzu.vmware.com/security/cve-2022-22969
- https://www.oracle.com/security-alerts/cpujul2022.html
