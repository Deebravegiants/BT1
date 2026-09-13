# [H] SwiftNIO NIOHTTP1:  HTTPDecoder accepts unbounded HTTP/1 header blocks, enabling remote DoS

## Summary
Severity: High
Advisory: GHSA-rj37-6j9x-74q6
CVE: CVE-2026-28980
CWE: CWE-400, CWE-770
Ecosystem: SwiftURL
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-12
Source: https://github.com/advisories/GHSA-rj37-6j9x-74q6
Type: github-advisory

## Affected
- SwiftURL: `github.com/apple/swift-nio` — affected >=0 <2.100.0

## Details
### Summary

The `HTTPDecoder` in `NIOHTTP1` enforces no limit on the total size of an HTTP/1 message's header block or on the number of header fields per message. A remote peer can submit an arbitrary number of small, valid headers in a single request and have them all accumulated into the resulting `HTTPHeaders` value before any application code runs. This can be used to exhaust memory, or — for consumers that subsequently convert headers into `swift-http-types`' `HTTPFields` — to crash the process.

### Details

`HTTPDecoder` previously enforced only a single hardcoded parsing limit: 80 KB per individual header field (name + value). There was no cap on the cumulative size of the header block, nor on the number of header fields per message. Because each individual field can remain well below the 80 KB threshold, a peer can submit hundreds of thousands of valid headers in a single request, all of which are appended to the decoded `HTTPHeaders` without bound.

The headers are then visible to user code through the standard `HTTPServerRequestPart.head` / `HTTPClientResponsePart.head` events. Two observed downstream effects:

  - **Hummingbird 2** (and other consumers that bridge `HTTPHeaders` into `swift-http-types`' `HTTPFields`) crashes via a precondition failure inside `HTTPFields` once the configured field count is exceeded.
  - **Vapor 4** does not crash, but the per-request memory footprint scales linearly with the number of headers received, allowing a single connection to inflate server memory use substantially.
  
### Impact

A single unauthenticated remote peer can trigger a denial of service against any HTTP/1 server (or, in the response direction, any HTTP/1 client) built on `NIOHTTP1` — either by crashing the process, depending on the downstream framework, or by driving the process's resident memory to arbitrary sizes.

### Patches

This issue is addressed in `swift-nio` 2.100.0 and later.

The `HTTPDecoder` now applies three parsing limits with conservative defaults, exposed through the new `NIOHTTPDecoderLimitConfiguration` type:

  | Limit | Default |
  | --- | --- |
  | `maxHeaderFieldSize` | 80 KB |
  | `maxHeaderListSize` | 2 MB |
  | `maxHeaderFieldCount` | 256 |

Exceeding any of these limits causes the decoder to fail with `HTTPParserError.headerOverflow`. The configuration can be supplied directly to `HTTPRequestDecoder` / `HTTPResponseDecoder`, or via the `decoderConfiguration` property on `NIOUpgradableHTTPServerPipelineConfiguration` and `NIOUpgradableHTTPClientPipelineConfiguration`.

Users who require larger limits — for example, applications that legitimately exchange very large header blocks — can opt into them explicitly by constructing a custom `NIOHTTPDecoderLimitConfiguration`.

### Workarounds

Users unable to upgrade can mitigate by placing a reverse proxy in front of the service that enforces equivalent limits on request header count and total header size.

### Credit

This issue was reported by @Joannis. SwiftNIO thanks @Joannis for the report and the support in landing the fix.

## References
- https://github.com/apple/swift-nio/security/advisories/GHSA-rj37-6j9x-74q6
- https://github.com/apple/swift-nio
