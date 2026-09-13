# [M] Spring Web Services: SOAP security faults leak Spring Security account state

## Summary
Severity: Medium
Advisory: GHSA-5x25-c2rf-f2jx
CVE: CVE-2026-40997
CWE: CWE-209
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-06-11
Source: https://github.com/advisories/GHSA-5x25-c2rf-f2jx
Type: github-advisory

## Affected
- Maven: `org.springframework.ws:spring-ws-security` — affected >=5.0.0 <5.0.2
- Maven: `org.springframework.ws:spring-ws-security` — affected >=4.1.0 <4.1.4
- Maven: `org.springframework.ws:spring-ws-security` — affected >=4.0.0
- Maven: `org.springframework.ws:spring-ws-security` — affected >=3.1.0

## Details
Several Spring WS integration paths with Spring Security could surface detailed account state (for example locked or disabled user semantics) to remote SOAP clients through exception messages or callback outcomes, instead of failing with generic authentication errors. That behavior assists remote attackers in distinguishing valid accounts from invalid ones and inferring lifecycle state.

Affected versions:
Spring Web Services 5.0.0 through 5.0.1; 4.1.0 through 4.1.3; 4.0.0 through 4.0.18; 3.1.0 through 3.1.8.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-40997
- https://github.com/spring-projects/spring-ws/commit/5051fae1a836c4d7fa12dedebdca23494764e421
- https://github.com/spring-projects/spring-ws
- https://spring.io/security/cve-2026-40997
