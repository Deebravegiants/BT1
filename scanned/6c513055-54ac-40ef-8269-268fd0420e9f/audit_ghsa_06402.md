# [H] gRPC-Go: Heap Memory Exhaustion (OOM) via HTTP/2 DATA Frame Fragmentation

## Summary
Severity: High
Advisory: GHSA-vp52-pcj8-j9qc
CVE: CVE-2026-84304
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-09-01
Source: https://github.com/advisories/GHSA-vp52-pcj8-j9qc
Type: github-advisory

## Affected
- Go: `google.golang.org/grpc` — affected >=0 <1.83.1

## Details
### Impact
An unauthenticated remote attacker can initiate a gRPC stream and purposefully fragment their payload into millions of tiny (e.g., 1-byte) HTTP/2 DATA frames. Even if the total payload volume falls within the configured connection and stream flow-control windows, each independent fragment incurs memory overhead due to internal tracking structures and queue allocation.

Repeated fragmentation massively inflates the heap space consumed by the stream. An attacker multiplexing multiple concurrent streams can exhaust the memory bounds of the runtime, forcing a runtime panic or OutOfMemory condition and leading to a remote Denial of Service (DoS).

### Patches
The change to fix this issue is merged in `master` and a patch release, 1.83.1, has been published that contains this fix.

### Workarounds
This vulnerability is mitigated by implementing receive buffer compaction. Consecutive small data buffers are automatically coalesced into larger buffers from a shared pool once the overhead is perceived to be excessive relative to actual payload data, drastically minimizing per-frame memory overheads.

This behavior is enabled by default. A temporary escape hatch is provided via the environment variable `GRPC_GO_EXPERIMENTAL_ENABLE_RECEIVE_BUFFER_COMPACTION=false` to disable the feature if unforeseen issues arise, but it will be removed in a future release.

## References
- https://github.com/grpc/grpc-go/security/advisories/GHSA-vp52-pcj8-j9qc
- https://nvd.nist.gov/vuln/detail/CVE-2026-84304
- https://github.com/grpc/grpc-go/pull/9331
- https://github.com/grpc/grpc-go/pull/9333
- https://github.com/grpc/grpc-go/commit/7354d9c8debb4bcf2225bf429857078de310c176
- https://github.com/grpc/grpc-go/commit/8cfeca0e1ee5ea0980dcc320e20240fa1079ec77
- https://github.com/grpc/grpc-go
- https://github.com/grpc/grpc-go/releases/tag/v1.83.1
