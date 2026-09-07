# [M] Netty HTTP/2: Advertised MAX_CONCURRENT_STREAMS are not enforced

## Summary
Severity: Medium
Advisory: GHSA-5x3r-wrvg-rp6q
CVE: CVE-2026-47244
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-06-08
Source: https://github.com/advisories/GHSA-5x3r-wrvg-rp6q
Type: github-advisory

## Affected
- Maven: `io.netty:netty-codec-http2` — affected >=4.2.0.Final <4.2.15.Final
- Maven: `io.netty:netty-codec-http2` — affected >=0 <4.1.135.Final

## Details
### Impact
DefaultHttp2Connection.DefaultEndpoint initialises maxActiveStreams/maxStreams to Integer.MAX_VALUE, and Http2Settings never inserts SETTINGS_MAX_CONCURRENT_STREAMS by default (Http2Settings.java:305-307 only clamps a user-supplied value). Unless the application explicitly calls initialSettings().maxConcurrentStreams(n), a Netty HTTP/2 server advertises no limit and enforces none locally. Each open stream allocates a DefaultStream object, PropertyMap slots, flow-controller state and IntObjectHashMap entry; with ~2^30 permissible odd stream IDs a single TCP connection can create hundreds of thousands of long-lived stream objects. This is also the precondition for CVE-2023-44487-style Rapid-Reset amplification, where the absence of a low concurrent cap multiplies backend work.

### Resources
https://www.rfc-editor.org/rfc/rfc7540.html#section-6.5.2

## References
- https://github.com/netty/netty/security/advisories/GHSA-5x3r-wrvg-rp6q
- https://nvd.nist.gov/vuln/detail/CVE-2026-47244
- https://github.com/netty/netty
- https://github.com/netty/netty/releases/tag/netty-4.1.135.Final
- https://github.com/netty/netty/releases/tag/netty-4.2.15.Final
