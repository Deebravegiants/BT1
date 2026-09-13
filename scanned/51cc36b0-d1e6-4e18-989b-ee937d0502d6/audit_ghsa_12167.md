# [M] Sliver Vulnerable to Authenticated OOM via Memory Exhaustion in mTLS/WireGuard Transports

## Summary
Severity: Medium
Advisory: GHSA-97vp-pwqj-46qc
CVE: CVE-2026-32941
CWE: CWE-770, CWE-789
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-03-17
Source: https://github.com/advisories/GHSA-97vp-pwqj-46qc
Type: github-advisory

## Affected
- Go: `github.com/bishopfox/sliver` — affected >=0

## Details
# Summary
A Remote OOM (Out-of-Memory) vulnerability exists in the Sliver C2 server's mTLS and WireGuard C2 transport layer. The `socketReadEnvelope` and `socketWGReadEnvelope` functions trust an attacker-controlled 4-byte length prefix to allocate memory, with `ServerMaxMessageSize` allowing single allocations of up to **~2 GiB**. A compromised implant or an attacker with valid credentials can exploit this by sending fabricated length prefixes over concurrent yamux streams (up to 128 per connection), forcing the server to attempt allocating **~256 GiB** of memory and triggering an OS OOM kill. This crashes the Sliver server, disrupts all active implant sessions, and may degrade or kill other processes sharing the same host. The same pattern also affects all implant-side readers, which have **no** upper-bound check at all.

---
# Root Cause Analysis

The C2 envelope framing protocol uses a 4-byte little-endian length prefix to delimit protobuf messages on the wire:

```
[raw_signature (74 bytes)] [uint32 length] [protobuf data]
```

In [socketReadEnvelope](https://github.com/BishopFox/sliver/blob/master/server/c2/mtls.go#L337-L392), after reading the length prefix, the server immediately allocates a buffer of the attacker-specified size:

```go
// server/c2/mtls.go
const ServerMaxMessageSize = (2 * 1024 * 1024 * 1024) - 1  // ~2 GiB

dataLength := int(binary.LittleEndian.Uint32(dataLengthBuf))
if dataLength <= 0 || ServerMaxMessageSize < dataLength {
    return nil, errors.New("[pivot] invalid data length")
}
dataBuf := make([]byte, dataLength)  // ← Allocates up to ~2 GiB

// ... data is read into buffer ...

// Envelope signature verification happens AFTER allocation and read:
if !ed25519.Verify(pubKey, dataBuf, signature) {
    return nil, errors.New("[mtls] invalid signature")
}
```

**Key issues:**

1. **Excessive limit**: `ServerMaxMessageSize` is set to `(2 * 1024 * 1024 * 1024) - 1` ≈ **2 GiB**, far exceeding any legitimate protobuf envelope (large payloads like screenshots and downloads are chunked at the RPC layer).
2. **Allocation before envelope verification**: While the TLS handshake validates the client certificate, the per-envelope ed25519 signature check (`ed25519.Verify`) occurs **after** the buffer allocation and `io.ReadFull`. Once the TLS connection is established, no further cryptographic proof is needed to trigger the allocation.
3. **Yamux amplification**: The yamux session allows up to `mtlsYamuxMaxConcurrentStreams = 128` concurrent streams. Each stream processes `socketReadEnvelope` independently, so a single connection can trigger **128 parallel ~2 GiB allocations**.
4. **Implant-side exposure**: The implant-side readers ([ReadEnvelope](https://github.com/BishopFox/sliver/blob/master/implant/sliver/transports/mtls/mtls.go#L184) in mTLS/WireGuard, [read()](https://github.com/BishopFox/sliver/blob/master/implant/sliver/pivots/pivots.go#L478) in pivots) have **no upper-bound check at all** — they accept any `dataLength > 0`.

The same pattern exists in [socketWGReadEnvelope](https://github.com/BishopFox/sliver/blob/master/server/c2/wireguard.go#L428-L487) for the WireGuard transport.


_Note: The same unbounded allocation pattern is also present in implant-side readers, though it poses no immediate risk to the server [1](https://github.com/BishopFox/sliver/blob/master/implant/sliver/transports/mtls/mtls.go#L185), [2](https://github.com/BishopFox/sliver/blob/master/implant/sliver/transports/wireguard/wireguard.go#L178), [3](https://github.com/BishopFox/sliver/blob/master/implant/sliver/pivots/pivots.go), [4](https://github.com/BishopFox/sliver/blob/master/implant/sliver/transports/pivotclients/pivotclient.go)._


---

# Proof of Concept
PoC Links: [mtls_poc.go](https://github.com/skoveit/Sliver-OOM-DoS-PoC/) or [Gist Version](https://gist.github.com/skoveit/08f3ec08ffbf3deeff189a83ef827dcf)
1. **Establish mTLS connection**: Complete a valid TLS 1.3 handshake presenting a valid implant client certificate.
2. **Negotiate yamux**: Send the `MUX/1` preface to enter multiplexed stream mode.
3. **Open concurrent streams**: Open multiple yamux streams (up to 128).
4. **Send malicious length prefix**: On each stream, send a 74-byte raw signature buffer followed by a 4-byte length prefix claiming `0x7FFFFFFF` (2,147,483,647 bytes ≈ 2 GiB). No actual data needs to follow.
5. **Result**: Each stream triggers a `make([]byte, 0x7FFFFFFF)` allocation. With 128 concurrent streams, the server process attempts to allocate **up to ~256 GiB** of memory, causing the OS OOM killer to terminate the process.

# Impact
- **Server availability**: The Sliver server process is killed. Active implant sessions are disrupted until the operator manually restarts the server.
- **Host degradation**: On hosts with swap enabled, the OOM event may cause swap thrashing and degrade other services sharing the same host before the process is killed.

## References
- https://github.com/BishopFox/sliver/security/advisories/GHSA-97vp-pwqj-46qc
- https://nvd.nist.gov/vuln/detail/CVE-2026-32941
- https://gist.github.com/skoveit/08f3ec08ffbf3deeff189a83ef827dcf
- https://github.com/BishopFox/sliver
