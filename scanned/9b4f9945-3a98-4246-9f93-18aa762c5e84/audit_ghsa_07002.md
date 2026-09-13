# [H] Netty XML: Injection / Risky Sink — unconfigured XML factory with active DTD and entity handling

## Summary
Severity: High
Advisory: GHSA-4qhr-g3c6-fcfx
CVE: CVE-2026-56817
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-4qhr-g3c6-fcfx
Type: github-advisory

## Affected
- Maven: `io.netty:netty-codec-xml` — affected >=4.2.0.Final <4.2.16.Final
- Maven: `io.netty:netty-codec-xml` — affected >=4.1.0.Final <4.1.136.Final

## Details
Any caller that can deliver bytes to a Netty channel pipeline containing `XmlDecoder` can send XML with a DOCTYPE declaration to a parser instantiated with no security configuration — but whether external entities are actually resolved depends on Aalto XML's async parser behavior, making this a confirmed misconfiguration with conditional exploitability.

## References
- https://github.com/netty/netty/security/advisories/GHSA-4qhr-g3c6-fcfx
- https://nvd.nist.gov/vuln/detail/CVE-2026-56817
- https://github.com/netty/netty/commit/5b68c61f37aa4a3045cba624cbea239655c9003b
- https://github.com/netty/netty/commit/bb2ff68a1fb71cb4b0eb9a9e17b66c52aff680c6
- https://github.com/netty/netty
- https://github.com/netty/netty/releases/tag/netty-4.1.136.Final
- https://github.com/netty/netty/releases/tag/netty-4.2.16.Final
