# [M] SwiftNIO HTTP/2: HTTP/2-to-HTTP/1 Request Smuggling via unvalidated :path pseudo-header in HTTP2ToHTTP1Codec

## Summary
Severity: Medium
Advisory: GHSA-4px2-pw77-vc85
CVE: CVE-2026-28898
CWE: CWE-116, CWE-444
Ecosystem: SwiftURL
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-06-12
Source: https://github.com/advisories/GHSA-4px2-pw77-vc85
Type: github-advisory

## Affected
- SwiftURL: `github.com/apple/swift-nio-http2` — affected >=0 <1.44.0

## Details
swift-nio-http2's HTTP/2-to-HTTP/1.1 codec (`HTTP2FramePayloadToHTTP1ServerCodec` / `HTTP2ToHTTP1ServerCodec`) did not validate pseudo-header values for control characters before placing them into the translated HTTP/1.1 message. A remote attacker could send an HTTP/2 request containing CR (\r), LF (\n), or NUL (\0) bytes in pseudo-header values such as `:path`, and when the server translated this to HTTP/1.1 — for example in a reverse-proxy configuration — the resulting output could contain injected headers or entirely smuggled requests.

This is an HTTP/2-to-HTTP/1.1 request smuggling vulnerability. HTTP/2's binary framing means that CRLF bytes are never parsed as line terminators at the HTTP/2 layer, so they pass through transparently to the HTTP/1.1 output. Any swift-nio-http2 server that translates HTTP/2 requests to HTTP/1.1 and forwards them to a backend is affected. Server-side Swift frameworks such as Vapor that use this codec in a reverse-proxy pattern are directly affected.

This vulnerability is related to https://github.com/advisories/GHSA-7fj7-39wj-c64f in swift-nio, which addressed CRLF injection in HTTP/1.1 header values but did not cover pseudo-header values in the HTTP/2 layer.

This vulnerability is also related to https://github.com/advisories/GHSA-cq87-8r7h-962v in swift-nio, which addressed CRLF injection in HTTP/1.1 version, method and path.

swift-nio-http2 1.44.0 adds validation of all pseudo-header values (:path, :authority, :scheme, :method, and :status) at both the HPACK header validation layer and the HTTP/2-to-HTTP/1.1 translation layer. Requests or responses containing CR, LF, or NUL bytes in any pseudo-header value are now rejected with a connection error.

SwiftNIO recommends all adopters upgrade to 1.44.0 as soon as possible.

SwiftNIO thanks @kuranikaran for filing this issue and the support in fixing it.

## References
- https://github.com/apple/swift-nio-http2/security/advisories/GHSA-4px2-pw77-vc85
- https://nvd.nist.gov/vuln/detail/CVE-2026-28898
- https://github.com/apple/swift-nio-http2/commit/61d1b44f6e4e118792be1cff88ee2bc0267c6f9a
- https://github.com/apple/swift-nio-http2
