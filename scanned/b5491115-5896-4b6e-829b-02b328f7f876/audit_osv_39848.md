# [M] UDP adapter sends ack to attacker-supplied host:port parsed from packet body, even when acknowledge=false

## Summary
Severity: Medium
Advisory: CVE-2026-47861
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-47861
Type: osv

## Details
An unauthenticated remote attacker who can send a single UDP packet to a Spring Integration UDP inbound adapter can cause the server to emit an outbound UDP datagram to an arbitrary internal or external host and port of the attacker's choosing.
Spring Integration 7.1.0
Spring Integration 7.0.0 - 7.0.5
Spring Integration 6.5.0 - 6.5.10
Spring Integration 6.4.0 - 6.4.12
Spring Integration 5.5.21 and earlier

## References
- https://spring.io/security/cve-2026-47861
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47861.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-47861
