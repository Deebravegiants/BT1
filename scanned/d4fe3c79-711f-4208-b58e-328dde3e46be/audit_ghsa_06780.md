# [H] Netty: HTTP/2 decompression leaks ByteBuf reference count when the decompressor channel is already closed (Direct memory leak / OOM DoS)

## Summary
Severity: High
Advisory: GHSA-93wv-jw9v-4972
CVE: CVE-2026-56819
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-31
Source: https://github.com/advisories/GHSA-93wv-jw9v-4972
Type: github-advisory

## Affected
- Maven: `io.netty:netty-codec-http2` — affected >=4.2.0 <4.2.16.Final
- Maven: `io.netty:netty-codec-http2` — affected >=4.1.0.Final <4.1.136.Final

## Details
### Summary

A remote, unauthenticated peer can leak one direct `ByteBuf` per HTTP/2 `DATA` frame in
applications that enable HTTP/2 content decompression via `DelegatingDecompressorFrameListener`.
When a `DATA` frame is processed for a stream whose decompressor has already been closed,
`Http2Decompressor.decompress(...)` retains the frame buffer but never releases it on the error
path, so its reference count never returns to zero. Repeating this over a long-lived HTTP/2
connection exhausts direct memory and crashes the JVM with `OutOfMemoryError` — a denial of service.

### Details

In `codec-http2/src/main/java/io/netty/handler/codec/http2/DelegatingDecompressorFrameListener.java`,
`Http2Decompressor.decompress(...)` does:

```java
// around line 433
decompressor.writeInbound(data.retain());
```

The argument `data.retain()` is evaluated **before** `writeInbound(...)` executes, incrementing the
buffer's reference count (`refCnt: 1 -> 2`). The very first statement of
`EmbeddedChannel.writeInbound(...)` is `ensureOpen()` (`EmbeddedChannel.java:360`), which throws
`ClosedChannelException` when the decompressor's internal `EmbeddedChannel` has already been closed.

When that happens:
- the `DATA` payload has been `retain()`ed but never entered the pipeline, so the decoder's
  `finally { release() }` never runs;
- the surrounding `catch (Throwable t)` block in `decompress(...)` (around line 451) does **not**
  release the extra reference;
- the input buffer therefore can never reach refCnt 0, and its (typically direct) memory is leaked.

The decompressor channel is closed on a reachable path:
`Http2Connection` `onStreamRemoved` → `Http2Decompressor.cleanup()` →
`EmbeddedChannel.finishAndReleaseAll()`
(`DelegatingDecompressorFrameListener.java:125-133` and `418-420`).

A peer that sends `DATA` frames for a stream whose decompressor has already been cleaned up (e.g.
continuing to send `DATA` after `END_STREAM` / stream removal) thus leaks one direct `ByteBuf` per
frame.

**Affected code**: `DelegatingDecompressorFrameListener.java`, method `Http2Decompressor.decompress(...)`
— the `decompressor.writeInbound(data.retain())` call (line ~433) and its `catch (Throwable t)`
block (line ~451), which lacks a `data.release()` rollback.

**Suggested fix**: track whether `writeInbound` succeeded and roll back the extra `retain()` only when
the data never entered the pipeline:

```java
boolean writeSucceeded = false;
try {
    decompressor.writeInbound(data.retain());
    writeSucceeded = true;            // pipeline now owns the release
    if (endOfStream) {
        decompressor.finish();
    }
    return 0;
} catch (Throwable t) {
    if (!writeSucceeded) {
        data.release();               // roll back the extra retain(); data never entered pipeline
    }
    if (t instanceof Http2Exception) {
        throw (Http2Exception) t;
    }
    throw streamError(stream.id(), INTERNAL_ERROR, t, ...);
}
```

| Case | writeSucceeded | catch action | Reason |
|------|:---:|---|---|
| `ensureOpen()` throws (this bug) | `false` | `data.release()` | data never entered pipeline |
| handler throws internally | `true` | no release | decoder `finally` already released |
| `finish()` throws | `true` | no release | `writeInbound` already succeeded |

### PoC

Reproduced against the official, unmodified `netty-codec-http2-4.2.15.Final.jar` from Maven Central,
using real netty classes and measuring `ByteBuf.refCnt()` directly (the leaking logic is not mocked).

Reproduction steps:

1. Download the official artifacts and their dependencies from Maven Central (version `4.2.15.Final`):
   `netty-common`, `netty-buffer`, `netty-transport`, `netty-resolver`, `netty-handler`,
   `netty-codec-base`, `netty-codec`, `netty-codec-http`, `netty-codec-http2`,
   `netty-codec-compression`.
2. Build a real `Http2Decompressor` wrapping a real gzip decoder `EmbeddedChannel`
   (`ZlibCodecFactory.newZlibDecoder(ZlibWrapper.GZIP)`).
3. Close the internal decompressor channel (equivalent to the end state of
   `cleanup()` / `finishAndReleaseAll()`).
4. Encode a real gzip `DATA` payload with `ZlibCodecFactory.newZlibEncoder(GZIP)` (`refCnt = 1`).
5. Call `decompress(...)` on the closed channel.
6. Observe: `writeInbound(...)` throws `ClosedChannelException` at its `ensureOpen()` entry
   (`EmbeddedChannel.java:360`), reached from `DelegatingDecompressorFrameListener.java:433`;
   `data.refCnt()` is now `2`.
7. Release once as the frame reader would; `refCnt` stays at `1` (`release()` returns `false`) → leaked.

Observed reference-count trace:

```
gzipData initial refCnt = 1
decompress -> data.retain()        -> refCnt = 2   (retain applied, never rolled back)
caller releases once               -> refCnt = 1   (release() returns false; not deallocated)
=> buffer never reaches 0 -> direct memory leaked
```

Observed exception stack (confirms the leak point):

```
java.nio.channels.ClosedChannelException
    at io.netty.channel.embedded.EmbeddedChannel.checkOpen(EmbeddedChannel.java:959)
    at io.netty.channel.embedded.EmbeddedChannel.ensureOpen(EmbeddedChannel.java:979)
    at io.netty.channel.embedded.EmbeddedChannel.writeInbound(EmbeddedChannel.java:360)
    at io.netty.handler.codec.http2.DelegatingDecompressorFrameListener$Http2Decompressor
            .decompress(DelegatingDecompressorFrameListener.java:433)
```

Two notes on the harness (they do not affect the leak mechanism):
- The internal channel is closed directly via `close()` rather than through `cleanup()`. The end
  state is identical (channel closed → `writeInbound` throws at `ensureOpen()`); the bug depends on
  "channel closed → retain not rolled back", not on *how* the channel was closed.
- In the isolated harness the rethrown `StreamException`'s root cause shows as `NullPointerException`
  because the harness does not initialise an `Http2LocalFlowController` (a secondary exception
  reported during channel close). The leak is already sealed at the `ClosedChannelException` thrown
  by `writeInbound`'s `ensureOpen()` (line 360); in a real server with the flow controller
  initialised, the triggering exception is the `ClosedChannelException` itself.

A complete self-contained PoC (`Verify02DecompressLeak.java`, ~150 lines, no test framework) plus the
exact `javac` / `java` commands can be attached on request.

### Impact

- **Vulnerability type**: uncontrolled resource consumption / memory leak (CWE-401), leading to
  denial of service. Each crafted `DATA` frame leaks one (typically direct/off-heap) `ByteBuf`.
- **Who is impacted**: any server (or client) that enables HTTP/2 content decompression by installing
  `DelegatingDecompressorFrameListener` in its HTTP/2 pipeline.
- **Attacker requirements**: remote, unauthenticated. The attacker only needs to send HTTP/2 `DATA`
  frames for a stream whose decompressor has been cleaned up (e.g. continue sending `DATA` after
  `END_STREAM`). No special server configuration beyond decompression being enabled.
- **Result**: sustained triggering over a long-lived connection exhausts direct memory and crashes
  the JVM with `OutOfMemoryError`.

## References
- https://github.com/netty/netty/security/advisories/GHSA-93wv-jw9v-4972
- https://nvd.nist.gov/vuln/detail/CVE-2026-56819
- https://github.com/netty/netty/commit/5b68c61f37aa4a3045cba624cbea239655c9003b
- https://github.com/netty/netty/commit/bb2ff68a1fb71cb4b0eb9a9e17b66c52aff680c6
- https://github.com/netty/netty
- https://github.com/netty/netty/releases/tag/netty-4.1.136.Final
- https://github.com/netty/netty/releases/tag/netty-4.2.16.Final
