# [H] gRPC Erlang package has unbounded request body accumulation in `read_full_body/3`

## Summary
Severity: High
Advisory: GHSA-q8gf-9rvj-gmgj
CVE: CVE-2026-48854
CWE: CWE-770
Ecosystem: Hex
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-25
Source: https://github.com/advisories/GHSA-q8gf-9rvj-gmgj
Type: github-advisory

## Affected
- Hex: `grpc` — affected >=0.3.1 <1.0.0

## Details
### Summary

`'Elixir.GRPC.Server.Adapters.Cowboy.Handler':read_full_body/3` accumulates every received chunk into a single growing binary with no size cap. When the client omits the `grpc-timeout` header, the read timeout resolves to `:infinity`, allowing a slow-trickle attacker to hold the connection open indefinitely while memory grows. A single unauthenticated connection is sufficient to exhaust BEAM memory and crash the node.

### Details

The read loop in `lib/grpc/server/adapters/cowboy/handler.ex` calls `:cowboy_req.read_body/2` in a recursive loop, concatenating each chunk: `body <> data`. There is no running-total check and no configurable maximum body size. As the loop drains the receive buffer, cowboy issues fresh HTTP/2 `WINDOW_UPDATE` frames, so the client can keep pushing data indefinitely.

The `grpc-timeout` header is attacker-supplied and optional. When absent, `timeout_left_opt(nil)` returns `:infinity`, so the per-chunk read also has no deadline. The two missing controls compound: a fast client can blast multi-gigabyte payloads directly into memory; a slow client can trickle data forever.

### PoC

1. Start any `grpc` server exposing a unary RPC (no special configuration required).
2. Open an HTTP/2 connection and send a POST to any unary RPC path with `Content-Type: application/grpc+proto` — omit the `grpc-timeout` header.
3. Stream a large body (e.g. 1 GiB) in chunks without sending the final `END_STREAM` flag immediately.
4. Observe BEAM memory growing proportionally to uploaded data with no server-side cap.

### Impact

Affects `grpc` ≥ 0.3.1. No authentication, no special configuration, and no specific RPC method required, the unbounded read is on the default unary ingress path.

### References

* Introduction commit: https://github.com/elixir-grpc/grpc/commit/d1abe70a6cad6dac4a3f8235d883d7c896989560
* Patch commit: https://github.com/elixir-grpc/grpc/commit/49e18c3ec6bb9afe2f712caad3dbab5c56a68a00

## References
- https://github.com/elixir-grpc/grpc/security/advisories/GHSA-q8gf-9rvj-gmgj
- https://nvd.nist.gov/vuln/detail/CVE-2026-48854
- https://github.com/elixir-grpc/grpc/pull/542
- https://github.com/elixir-grpc/grpc/commit/49e18c3ec6bb9afe2f712caad3dbab5c56a68a00
- https://cna.erlef.org/cves/CVE-2026-48854.html
- https://github.com/elixir-grpc/grpc
- https://github.com/elixir-grpc/grpc/releases/tag/v1.0.0
- https://osv.dev/vulnerability/EEF-CVE-2026-48854
