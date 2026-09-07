# [M] Netty: [codec-http2] Lack of Host Header Deduplication in HTTP/2→HTTP/1.x Translation Leads to Request Routing Bypass

## Summary
Severity: Medium
Advisory: GHSA-c69g-56f8-xwqj
CVE: CVE-2026-59900
CWE: CWE-444
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-c69g-56f8-xwqj
Type: github-advisory

## Affected
- Maven: `io.netty:netty-codec-http2` — affected >=4.2.0.Final <4.2.16.Final
- Maven: `io.netty:netty-codec-http2` — affected >=0 <4.1.136.Final

## Details
Netty's HTTP/2-to-HTTP/1.x translation layer (`Http2StreamFrameToHttpObjectCodec` and `InboundHttp2ToHttpAdapter`) fails to deduplicate or validate `Host` headers when an HTTP/2 client supplies both the `:authority` pseudo-header and a literal `host` header in a single HEADERS frame. The translator maps `:authority` to `Host` and separately copies the literal `host` header, producing an `HttpRequest` object containing two `Host` headers with attacker-controlled differing values.

## References
- https://github.com/netty/netty/security/advisories/GHSA-c69g-56f8-xwqj
- https://github.com/netty/netty
- https://github.com/netty/netty/releases/tag/netty-4.1.136.Final
- https://github.com/netty/netty/releases/tag/netty-4.2.16.Final
