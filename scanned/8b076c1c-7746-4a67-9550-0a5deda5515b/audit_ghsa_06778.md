# [M] mint: Content-Length header accepts non-RFC "+" sign prefix

## Summary
Severity: Medium
Advisory: GHSA-mjqx-c6f6-7rc2
CVE: CVE-2026-49753
CWE: CWE-444
Ecosystem: Hex
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:L/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-07-09
Source: https://github.com/advisories/GHSA-mjqx-c6f6-7rc2
Type: github-advisory

## Affected
- Hex: `mint` — affected >=0 <1.9.0

## Details
### Summary

Mint's HTTP/1 client accepts `Content-Length` header values with a leading `+` sign (e.g. `+0`, `+123`), which RFC 7230 forbids (`Content-Length = 1*DIGIT`). On a connection shared with a strict fronting proxy or load balancer, this parser disagreement is a response-smuggling primitive: the proxy frames the body one way, Mint frames it another, and bytes meant for one response leak into the next consumer's response stream.

### Details

`'Elixir.Mint.HTTP1.Parse':content_length_header/1` in `lib/mint/http1/parse.ex` parses the header value with `Integer.parse/1`. By design, `Integer.parse/1` accepts an optional `+` or `-` sign prefix. The `length >= 0` guard rules out negatives, but inputs such as `"+0"`, `"+123"`, or `"+1"` pass through and are returned as valid lengths.

A strict proxy or load balancer rejects or reframes `Content-Length: +0\r\n`, while Mint silently treats it as `0`. When Mint reuses the socket (keep-alive, pipelining, or any pooled connection) and the connection is shared with a proxy that frames the same bytes differently, trailing bytes the proxy attributes to response N are attributed by Mint to response N+1. Across trust boundaries (shared pools, multi-tenant fronting) this enables response smuggling.

### PoC

1. Stand up a raw TCP server that returns `HTTP/1.1 200 OK\r\nContent-Length: +0\r\nConnection: keep-alive\r\n\r\n<smuggled bytes>`.
2. Connect a Mint HTTP/1 client to the server and issue a request.
3. Observe that Mint reports the response as status 200 with `Content-Length: "+0"` and an empty body, leaving the smuggled bytes sitting in the socket buffer for the next response.

### Impact

Response-smuggling / request-response desync primitive in Mint's HTTP/1 client parser. Anyone using Mint (directly or via Finch, Tesla's Mint adapter, Req, etc.) to talk through a shared or pooled connection where a fronting proxy enforces RFC 7230 strictly while Mint does not is exposed. The attacker is the response producer (a malicious or compromised upstream, or anything that can inject bytes into a shared origin response); exploitation into a cross-request data leak additionally requires the deployment to share a Mint connection across trust boundaries.

## Resources

* Introduction commit: https://github.com/elixir-mint/mint/commit/65e0e86d799a6d3b08e4372fccdd9747535e0dd6
* Patch commit: https://github.com/elixir-mint/mint/commit/47e48027480228e4e32a0b4df39db497b4804921

## References
- https://github.com/elixir-mint/mint/security/advisories/GHSA-mjqx-c6f6-7rc2
- https://nvd.nist.gov/vuln/detail/CVE-2026-49753
- https://github.com/elixir-mint/mint/commit/47e48027480228e4e32a0b4df39db497b4804921
- https://cna.erlef.org/cves/CVE-2026-49753.html
- https://github.com/elixir-mint/mint
- https://osv.dev/vulnerability/EEF-CVE-2026-49753
