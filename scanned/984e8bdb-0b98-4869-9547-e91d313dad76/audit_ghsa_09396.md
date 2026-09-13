# [H] Netty has HttpClientCodec response desynchronization

## Summary
Severity: High
Advisory: GHSA-57rv-r2g8-2cj3
CVE: CVE-2026-42584
CWE: CWE-444
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-57rv-r2g8-2cj3
Type: github-advisory

## Affected
- Maven: `io.netty:netty-codec-http` — affected >=4.2.0.Alpha1 <4.2.13.Final
- Maven: `io.netty:netty-codec-http` — affected >=0 <4.1.133.Final

## Details
### Summary
 If HttpClientCodec is configured, there are use cases when a response body from one request, can be parsed as another's.

### Details
HttpClientCodec pairs each inbound response with an outbound request by `queue.poll()` once per response, including for `1xx`. If the client pipelines GET then HEAD and the server sends 103, then 200 with GET body, then 200 for HEAD, the queue pairs HEAD with the first 200. The HEAD rule then skips reading that message’s body, so the GET entity bytes stay on the stream and the following 200 is parsed from the wrong offset.

Prerequisites 
- HTTP/1.1 pipelining
- HEAD in the pipeline
- The server sends 1xx

### PoC

```java
    @Test
    public void test() {
        EmbeddedChannel channel = new EmbeddedChannel(new HttpClientCodec());

        assertTrue(channel.writeOutbound(new DefaultFullHttpRequest(HttpVersion.HTTP_1_1, HttpMethod.GET, "/1")));
        ByteBuf request = channel.readOutbound();
        request.release();
        assertNull(channel.readOutbound());

        assertTrue(channel.writeOutbound(new DefaultFullHttpRequest(HttpVersion.HTTP_1_1, HttpMethod.HEAD, "/2")));
        request = channel.readOutbound();
        request.release();
        assertNull(channel.readOutbound());

        String responseStr = "HTTP/1.1 103 Early Hints\r\n\r\n" +
                "HTTP/1.1 200 OK\r\nContent-Length: 5\r\n\r\nhello" +
                "HTTP/1.1 200 OK\r\n\r\n";
        assertTrue(channel.writeInbound(Unpooled.copiedBuffer(responseStr, CharsetUtil.US_ASCII)));

        // Response 1
        HttpResponse response = channel.readInbound();
        assertEquals(HttpResponseStatus.EARLY_HINTS, response.status());
        LastHttpContent last = channel.readInbound();
        assertEquals(0, last.content().readableBytes());
        last.release();

        // Response 2
        response = channel.readInbound();
        assertEquals(HttpResponseStatus.OK, response.status());
        last = channel.readInbound();
        assertEquals(0, last.content().readableBytes());
        last.release();

        // Response 3
        FullHttpResponse response1 = channel.readInbound();
        assertTrue(response1.decoderResult().isFailure());
        assertEquals(0, response1.content().readableBytes());
        response1.release();

        assertFalse(channel.finish());
    }
```

### Impact
Integrity/availability of HTTP parsing on that connection, unsafe reuse of the socket.

## References
- https://github.com/netty/netty/security/advisories/GHSA-57rv-r2g8-2cj3
- https://nvd.nist.gov/vuln/detail/CVE-2026-42584
- https://github.com/netty/netty
