# [H] Netty: Denial of Service in XmlFrameDecoder via CPU Exhaustion

## Summary
Severity: High
Advisory: GHSA-v74w-7mr3-4qg3
CVE: CVE-2026-73507
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-v74w-7mr3-4qg3
Type: github-advisory

## Affected
- Maven: `io.netty:netty-codec-xml` — affected >=4.2.0.Final <4.2.16.Final
- Maven: `io.netty:netty-codec-xml` — affected >=0 <4.1.136.Final

## Details
### Summary
An attacker can cause Denial of Service by sending a specially crafted malicious XML payload (e.g., repeated `</` characters) to a Netty server utilizing XmlFrameDecoder, causing the server's EventLoop thread to exhaust CPU resources and become unresponsive.

### Details
`io.netty.handler.codec.xml.XmlFrameDecoder` suffers from a vulnerability resulting in CPU exhaustion. When `<` followed by `/` is encountered, the decoder scans the remaining buffer for a closing `>`.
Because the parser state is not saved between `decode()` invocations, an attacker can trickle-feed a payload of `</` characters. This forces the decoder to repeatedly rescan the entire accumulated buffer. A 1MB `maxFrameLength` is enough to completely hang a server's thread while it loops endlessly.

### Impact
Denial of Service via CPU Exhaustion. Any application utilizing Netty's XmlFrameDecoder is impacted. An unauthenticated remote attacker can exploit this flaw by sending a modest amount of malformed XML data to an exposed port.

## References
- https://github.com/netty/netty/security/advisories/GHSA-v74w-7mr3-4qg3
- https://github.com/netty/netty/pull/17063
- https://github.com/netty/netty/pull/17065
- https://github.com/netty/netty/commit/5b68c61f37aa4a3045cba624cbea239655c9003b
- https://github.com/netty/netty/commit/bb2ff68a1fb71cb4b0eb9a9e17b66c52aff680c6
- https://github.com/netty/netty
- https://github.com/netty/netty/releases/tag/netty-4.1.136.Final
- https://github.com/netty/netty/releases/tag/netty-4.2.16.Final
