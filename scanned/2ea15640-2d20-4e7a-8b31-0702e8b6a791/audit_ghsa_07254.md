# [H] Netty SPDY zlib header block continues decoded expansion after maxHeaderSize truncation

## Summary
Severity: High
Advisory: GHSA-mvh2-crg5-v77c
CVE: CVE-2026-55833
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-mvh2-crg5-v77c
Type: github-advisory

## Affected
- Maven: `io.netty:netty-codec-http` — affected >=4.2.0.Final <4.2.16.Final
- Maven: `io.netty:netty-codec-http` — affected >=4.1.0.Final <4.1.136.Final

## Details
### Summary
Netty SPDY header decoding continues inflating zlib-compressed header blocks after the raw header parser has already exceeded maxHeaderSize and marked the frame truncated. At commit b2d2137c4404af425bf9d5d601a62576f5c06925, a 12,253-byte compressed SPDY header block can declare and inflate a 12 MiB header-name field with maxHeaderSize=16, forcing compression-amplified decode and skip work in a reachable SpdyFrameCodec pipeline.

### PoC
[poc.zip](https://github.com/user-attachments/files/28445780/poc.zip)

run with:
```bash
bash ./poc/run.sh
```
expected output:
```text
NETTY_SPDY_ZLIB_DECODED_AFTER_LIMIT_TRIGGERED compressed_bytes=12253 declared_name_length=12582912 max_header_size=16 truncated=true invalid=false
```

The fingerprint means the compressed input was fully consumed while the raw header parser ended with `truncated=true` and `invalid=false` after processing the oversized decoded name. That specific state distinguishes this bug from a generic setup failure: the maxHeaderSize guard fired, but the zlib/raw decode path still inflated and skipped the full 12 MiB declared name.

### Impact
A remote unauthenticated peer that can speak SPDY to a Netty pipeline containing SpdyFrameCodec can send a small compressed HEADERS block that expands into much larger raw header data after the configured maxHeaderSize limit has already been exceeded. The attack requires a reachable SPDY codec, ordinary transport setup such as TCP and optional TLS, and no independent compressed-frame-size or connection-rate limit ahead of SpdyFrameCodec. The satisfied protocol guards are straightforward: the HEADERS frame uses a nonzero stream id and length >= 4, the decoder factory selects the zlib decoder, the payload uses the SPDY dictionary, and the raw block appends a zero-length value so the already-truncated frame reaches END_HEADER_BLOCK. The user-visible effect is denial of service through compression-amplified CPU and allocation churn.

## References
- https://github.com/netty/netty/security/advisories/GHSA-mvh2-crg5-v77c
- https://nvd.nist.gov/vuln/detail/CVE-2026-55833
- https://github.com/netty/netty/commit/5b68c61f37aa4a3045cba624cbea239655c9003b
- https://github.com/netty/netty/commit/bb2ff68a1fb71cb4b0eb9a9e17b66c52aff680c6
- https://github.com/netty/netty
- https://github.com/netty/netty/releases/tag/netty-4.1.136.Final
- https://github.com/netty/netty/releases/tag/netty-4.2.16.Final
