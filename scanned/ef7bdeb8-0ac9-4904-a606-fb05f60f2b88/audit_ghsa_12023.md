# [H] Netty HTTP/2 CONTINUATION Frame Flood DoS via Zero-Byte Frame Bypass

## Summary
Severity: High
Advisory: GHSA-w9fj-cfpg-grvv
CVE: CVE-2026-33871
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-w9fj-cfpg-grvv
Type: github-advisory

## Affected
- Maven: `io.netty:netty-codec-http2` — affected >=0 <4.1.132.Final
- Maven: `io.netty:netty-codec-http2` — affected >=4.2.0.Alpha1 <4.2.11.Final

## Details
### Summary
A remote user can trigger a Denial of Service (DoS) against a Netty HTTP/2 server by sending a flood of `CONTINUATION` frames. The server's lack of a limit on the number of `CONTINUATION` frames, combined with a bypass of existing size-based mitigations using zero-byte frames, allows an user to cause excessive CPU consumption with minimal bandwidth, rendering the server unresponsive.

### Details
The vulnerability exists in Netty's `DefaultHttp2FrameReader`. When an HTTP/2 `HEADERS` frame is received without the `END_HEADERS` flag, the server expects one or more subsequent `CONTINUATION` frames. However, the implementation does not enforce a limit on the *count* of these `CONTINUATION` frames.

The key issue is located in `codec-http2/src/main/java/io/netty/handler/codec/http2/DefaultHttp2FrameReader.java`. The `verifyContinuationFrame()` method checks for stream association but fails to implement a frame count limit.

Any user can exploit this by sending a stream of `CONTINUATION` frames with a zero-byte payload. While Netty has a `maxHeaderListSize` protection to limit the total size of headers, this check is never triggered by zero-byte frames. The logic effectively evaluates to `maxHeaderListSize - 0 < currentSize`, which will not trigger the limit until a non-zero byte is added. As a result, the server is forced to process an unlimited number of frames, consuming a CPU thread and monopolizing the connection.

`codec-http2/src/main/java/io/netty/handler/codec/http2/DefaultHttp2FrameReader.java`

**`verifyContinuationFrame()` (lines 381-393)** — No frame count check:
```java
private void verifyContinuationFrame() throws Http2Exception {
    verifyAssociatedWithAStream();
    if (headersContinuation == null) {
        throw connectionError(PROTOCOL_ERROR, "...");
    }
    if (streamId != headersContinuation.getStreamId()) {
        throw connectionError(PROTOCOL_ERROR, "...");
    }
    // NO frame count limit!
}
```

**`HeadersBlockBuilder.addFragment()` (lines 695-723)** — Byte limit bypassed by 0-byte frames:
```java
// Line 710-711: This check NEVER fires when len=0
if (headersDecoder.configuration().maxHeaderListSizeGoAway() - len <
        headerBlock.readableBytes()) {
    headerSizeExceeded();  // 10240 - 0 < 1 => FALSE always
}
```

When `len=0`: `maxGoAway - 0 < readableBytes` → `10240 < 1` → FALSE. The byte limit is never triggered.

### Impact
This is a CPU-based Denial of Service (DoS). Any service using Netty's default HTTP/2 server implementation is impacted. An unauthenticated user can exhaust server CPU resources and block legitimate users, leading to service unavailability. The low bandwidth requirement for the attack makes it highly practical.

## References
- https://github.com/netty/netty/security/advisories/GHSA-w9fj-cfpg-grvv
- https://nvd.nist.gov/vuln/detail/CVE-2026-33871
- https://github.com/netty/netty
