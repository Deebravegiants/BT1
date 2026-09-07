# [M] Spring Framework STOMP over WebSocket applications may allow attackers to send unauthorized messages

## Summary
Severity: Medium
Advisory: GHSA-7fch-4f2f-jcgm
CVE: CVE-2025-41254
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2025-10-16
Source: https://github.com/advisories/GHSA-7fch-4f2f-jcgm
Type: github-advisory

## Affected
- Maven: `org.springframework:spring-websocket` — affected >=6.2.0 <6.2.12
- Maven: `org.springframework:spring-websocket` — affected >=6.1.0
- Maven: `org.springframework:spring-websocket` — affected >=6.0.0
- Maven: `org.springframework:spring-websocket` — affected >=0

## Details
STOMP over WebSocket applications may be vulnerable to a security bypass that allows an attacker to send unauthorized messages.

### Affected Spring Products and Versions
Spring Framework:

  *  6.2.0 - 6.2.11
  *  6.1.0 - 6.1.23
  *  6.0.x - 6.0.29
  *  5.3.0 - 5.3.45
  *  Older, unsupported versions are also affected.


### Mitigation
Users of affected versions should upgrade to the corresponding fixed version.

### Affected version(s)
Fix version | Availability
-|-
6.2.x | 6.2.12 OSS
6.1.x | 6.1.24 Commercial https://enterprise.spring.io/
6.0.x | N/A Out of support https://spring.io/projects/spring-framework#support
5.3.x | 5.3.46 Commercial https://enterprise.spring.io/

No further mitigation steps are necessary.

CreditThis vulnerability was discovered and responsibly reported by Jannis Kaiser.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-41254
- https://github.com/spring-projects/spring-framework
- https://nvd.nist.gov/vuln-metrics/cvss/v3-calculator?vector=AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N&version=3.1
- https://spring.io/security/cve/2025-41254
