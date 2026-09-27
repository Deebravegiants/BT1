# [H] Spring Web Services: SSRF via unvalidated WS-Addressing reply destinations

## Summary
Severity: High
Advisory: GHSA-whpp-xv3h-rwxf
CVE: CVE-2026-40999
CWE: CWE-918
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-11
Source: https://github.com/advisories/GHSA-whpp-xv3h-rwxf
Type: github-advisory

## Affected
- Maven: `org.springframework.ws:spring-ws-core` — affected >=5.0.0 <5.0.2
- Maven: `org.springframework.ws:spring-ws-core` — affected >=4.1.0 <4.1.4
- Maven: `org.springframework.ws:spring-ws-core` — affected >=4.0.0
- Maven: `org.springframework.ws:spring-ws-core` — affected >=3.1.0

## Details
When WS-Addressing is used with non-anonymous ReplyTo or FaultTo addresses, Spring WS may initiate outbound connections through configured WebServiceMessageSender instances to destinations taken directly from request headers without verifying that those destinations are safe to connect to.

Affected versions:
Spring Web Services 5.0.0 through 5.0.1; 4.1.0 through 4.1.3; 4.0.0 through 4.0.18; 3.1.0 through 3.1.8.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-40999
- https://github.com/spring-projects/spring-ws/commit/5121a4e545803c4925e63c4ed015391be2605ba5
- https://github.com/spring-projects/spring-ws
- https://spring.io/security/cve-2026-40999
