# [H] io.netty:netty-codec-http2 vulnerable to HTTP/2 Rapid Reset Attack

## Summary
Severity: High
Advisory: GHSA-xpw8-rcwv-8f8p
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-10-10
Source: https://github.com/advisories/GHSA-xpw8-rcwv-8f8p
Type: github-advisory

## Affected
- Maven: `io.netty:netty-codec-http2` — affected >=0 <4.1.100.Final

## Details
A client might overload the server by issue frequent RST frames. This can cause a massive amount of load on the remote system and so cause a DDOS attack. 

### Impact
This is a DDOS attack, any http2 server is affected and so you should update as soon as possible.

### Patches
This is patched in version 4.1.100.Final.

### Workarounds
A user can limit the amount of RST frames that are accepted per connection over a timeframe manually using either an own `Http2FrameListener` implementation or an `ChannelInboundHandler` implementation (depending which http2 API is used).

### References
- https://www.cve.org/CVERecord?id=CVE-2023-44487
- https://blog.cloudflare.com/technical-breakdown-http2-rapid-reset-ddos-attack/
- https://cloud.google.com/blog/products/identity-security/google-cloud-mitigated-largest-ddos-attack-peaking-above-398-million-rps/

## References
- https://github.com/apple/swift-nio-http2/security/advisories/GHSA-qppj-fm5r-hxr3
- https://github.com/netty/netty/security/advisories/GHSA-xpw8-rcwv-8f8p
- https://nvd.nist.gov/vuln/detail/CVE-2023-44487
- https://github.com/netty/netty/commit/58f75f665aa81a8cbcf6ffa74820042a285c5e61
- https://github.com/netty/netty
- https://www.cve.org/CVERecord?id=CVE-2023-44487
