# [M] Netty: WebSockets V07/V08 handshaker missing Connection/Upgrade validation

## Summary
Severity: Medium
Advisory: GHSA-4mp9-239f-g9hg
CVE: CVE-2026-59898
CWE: CWE-444
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-4mp9-239f-g9hg
Type: github-advisory

## Affected
- Maven: `io.netty:netty-codec-http` — affected >=4.2.0.Final <4.2.16.Final
- Maven: `io.netty:netty-codec-http` — affected >=0 <4.1.136.Final

## Details
## Summary
An attacker can force WebSocket upgrade via the lax V07 (or V08) handshaker by sending `Sec-WebSocket-Version: 7` and omitting `Connection: Upgrade` / `Upgrade: websocket` headers, completing a protocol switch that a proxy would not recognize as an Upgrade request and enabling HTTP request smuggling / protocol-confusion attacks.

## References
- https://github.com/netty/netty/security/advisories/GHSA-4mp9-239f-g9hg
- https://github.com/netty/netty
- https://github.com/netty/netty/releases/tag/netty-4.1.136.Final
- https://github.com/netty/netty/releases/tag/netty-4.2.16.Final
