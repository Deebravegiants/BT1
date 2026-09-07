# [M] Spring Web Services: X.509 authentication bypasses Spring Security account checks

## Summary
Severity: Medium
Advisory: GHSA-6mfm-98wv-32wm
CVE: CVE-2026-40995
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-11
Source: https://github.com/advisories/GHSA-6mfm-98wv-32wm
Type: github-advisory

## Affected
- Maven: `org.springframework.ws:spring-ws-security` — affected >=5.0.0 <5.0.2
- Maven: `org.springframework.ws:spring-ws-security` — affected >=4.1.0 <4.1.4
- Maven: `org.springframework.ws:spring-ws-security` — affected >=4.0.0
- Maven: `org.springframework.ws:spring-ws-security` — affected >=3.1.0

## Details
X509AuthenticationProvider could issue a fully authenticated X509AuthenticationToken when a presented certificate mapped to UserDetails, without applying Spring Security's standard account lifecycle checks (disabled, locked, expired, or credentials-expired accounts).

Affected versions:
Spring Web Services 5.0.0 through 5.0.1; 4.1.0 through 4.1.3; 4.0.0 through 4.0.18; 3.1.0 through 3.1.8.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-40995
- https://github.com/spring-projects/spring-ws/commit/e5dc311359e14f5b25bcb33f20d43cc3513e9d10
- https://github.com/spring-projects/spring-ws
- https://spring.io/security/cve-2026-40995
