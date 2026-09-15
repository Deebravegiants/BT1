# [M] swift-nio-http2: Missing CR/LF/NUL validation in header values

## Summary
Severity: Medium
Advisory: GHSA-q3g2-m552-3r9c
CVE: CVE-2026-64785
CWE: CWE-113, CWE-444
Ecosystem: SwiftURL
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-q3g2-m552-3r9c
Type: github-advisory

## Affected
- SwiftURL: `swift-nio-http2` — affected >=0 <1.45.0

## Details
## Summary

SwiftNIO HTTP/2 was missing validation on inbound HEADERS frames that let
CR, LF, NUL, SP and other control characters reach an HTTP/1.1 backend
through NIOHTTP2's HTTP/2-to-HTTP/1 codec, enabling HTTP request smuggling
or response splitting.

## Impact

Two related gaps in inbound header validation, against any application
using HTTP2ToHTTP1Codec (or HTTP2FramePayloadToHTTP1Codec) to front an
HTTP/1.1 backend:

Regular header field values were only checked against a forbidden-name
list (connection, transfer-encoding, proxy-connection, keep-alive,
upgrade); the value itself was never inspected. An attacker-controlled
regular header field value containing CR or LF passed validation and, once
serialized as `name: value CRLF` by the codec, terminated the field early
and injected extra header lines into the outbound HTTP/1.1 message.

Pseudo-header values (`:path` in particular) were only checked against
CR, LF and NUL. A `:path` value containing SP serializes into the
request-target of `METHOD SP request-target SP HTTP-version CRLF`, so a
value like `/a HTTP/1.1` produces `GET /a HTTP/1.1 HTTP/1.1` — a
parser-differential request line depending on whether a downstream reader
takes the first or last SP-delimited token as the version.

Neither of these is reachable on a stock pipeline: NIOHTTP1's outbound
validator (`enableOutboundHeaderValidation`, on by default) already rejects
these characters on write. The exposure is pipelines that skip outbound
validation, or any code that reads validated-looking `HTTPRequestHead.headers`
and forwards the values on trusting that HTTP/2 already checked them.

## Fix

Fixed in 48bfd90 and 45bdf67.

## Mitigation

Upgrade to 1.45.0

## References
- https://github.com/apple/swift-nio-http2/security/advisories/GHSA-q3g2-m552-3r9c
- https://nvd.nist.gov/vuln/detail/CVE-2026-64785
- https://github.com/apple/swift-nio-http2/commit/45bdf670248be5f16ec0340e125dca285536f0fb
- https://github.com/apple/swift-nio-http2/commit/48bfd9067d7d1d15c4789440127a0cf36222ea43
- https://github.com/apple/swift-nio-http2
- https://github.com/apple/swift-nio-http2/releases/tag/1.45.0
