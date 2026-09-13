# [H] Spring Web Services: Wss4jSecurityInterceptor disables WS-I BSP validation by default

## Summary
Severity: High
Advisory: GHSA-gg9r-wr4p-w63h
CVE: CVE-2026-40994
CWE: CWE-1188
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2026-06-11
Source: https://github.com/advisories/GHSA-gg9r-wr4p-w63h
Type: github-advisory

## Affected
- Maven: `org.springframework.ws:spring-ws-security` — affected >=5.0.0 <5.0.2
- Maven: `org.springframework.ws:spring-ws-security` — affected >=4.1.0 <4.1.4
- Maven: `org.springframework.ws:spring-ws-security` — affected >=4.0.0
- Maven: `org.springframework.ws:spring-ws-security` — affected >=3.1.0

## Details
Wss4jSecurityInterceptor initialized its BSP (WS-I Basic Security Profile) compliance flag so that inbound validation disabled WSS4J BSP enforcement on RequestData. Services that validate WS-Security on the network could therefore accept messages that violate BSP rules, weakening protocol-level checks.

Affected versions:
Spring Web Services 5.0.0 through 5.0.1; 4.1.0 through 4.1.3; 4.0.0 through 4.0.18; 3.1.0 through 3.1.8.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-40994
- https://github.com/spring-projects/spring-ws
- https://spring.io/security/cve-2026-40994
